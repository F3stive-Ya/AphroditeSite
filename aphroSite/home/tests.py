import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from .cipher import CipherOutput, GREEK_GLYPHS, encrypt_true_thoughts


class HomePageTests(TestCase):
	def test_home_page_renders_templates(self):
		response = self.client.get('/')

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/index.html')
		self.assertTemplateUsed(response, 'base.html')
		self.assertContains(response, '<h1 id="profile-name">Aphrodite (Ἀφροδίτη)</h1>')
		self.assertContains(response, 'Full marble statue of Aphrodite')
		self.assertContains(response, 'The force that draws the world together.')
		self.assertContains(response, 'Profile / Home')
		self.assertContains(response, 'href="/magic/"')
		self.assertContains(response, 'href="/info/"')
		self.assertContains(response, 'Domains')

	def test_profile_includes_journal(self):
		response = self.client.get('/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="blog"')
		self.assertContains(response, 'The most beautiful woman!')
		self.assertContains(response, 'Prayers from Lesbos')
		self.assertNotContains(response, 'nav-link-label">Blog</span>')
		self.assertContains(response, 'Liked by</span> Eros, Psyche')
		self.assertContains(response, 'Liked by</span> The Muses, The Graces')

	def test_info_page_links_to_journal(self):
		response = self.client.get('/info/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'THE JOURNAL')
		self.assertContains(response, 'href="/#blog">Visit the blog</a>')

	def test_magic_and_info_pages_render(self):
		for path, heading in [('/magic/', "Aphrodite's Magic Girdle"), ('/info/', 'Info')]:
			with self.subTest(path=path):
				response = self.client.get(path)
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, f'<h1>{heading}</h1>')

	@patch('home.views.encrypt_true_thoughts')
	def test_magic_form_displays_ciphertext_and_greek_key(self, encrypt_true_thoughts):
		encrypt_true_thoughts.return_value = CipherOutput('CIPHERTEXT', 'GREEK-DECOY')

		response = self.client.post('/magic/', {'thoughts': 'A true thought'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'CIPHERTEXT')
		self.assertContains(response, 'cipher-text-letters')
		self.assertContains(response, 'GREEK-DECOY')
		self.assertContains(response, 'ANCIENT GREEK')
		self.assertContains(response, 'A true thought')
		response_html = response.content.decode()
		self.assertLess(response_html.index('01 / PLAINTEXT'), response_html.index('02 / ANCIENT GREEK'))
		self.assertLess(response_html.index('02 / ANCIENT GREEK'), response_html.index('03 / CIPHERTEXT'))
		encrypt_true_thoughts.assert_called_once_with('A true thought')


class CipherTests(SimpleTestCase):
	@patch('home.cipher.secrets.choice', return_value=GREEK_GLYPHS[0])
	def test_encrypts_submitted_letters_and_preserves_formatting(self, choose_glyph):
		result = encrypt_true_thoughts('A b!')

		self.assertEqual(result.ciphertext, 'A q!')
		self.assertEqual(result.decoy_greek, GREEK_GLYPHS[0] * 2)
		self.assertEqual(choose_glyph.call_count, 2)


class BuildStaticTests(SimpleTestCase):
	def test_build_static_exports_pages_and_assets_with_base_url(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			output_dir = Path(tmpdir) / 'site'
			call_command('build_static', output=str(output_dir), base_url='/GodsDev/')

			self.assertTrue((output_dir / '.nojekyll').exists())
			self.assertTrue((output_dir / 'index.html').exists())
			self.assertTrue((output_dir / 'magic' / 'index.html').exists())
			self.assertTrue((output_dir / 'info' / 'index.html').exists())
			self.assertTrue((output_dir / 'static' / 'home' / 'site.css').exists())
			self.assertTrue((output_dir / 'static' / 'home' / 'magic.js').exists())
			self.assertFalse((output_dir / 'static' / 'admin').exists())

			index_html = (output_dir / 'index.html').read_text(encoding='utf-8')
			self.assertIn('href="/GodsDev/static/home/site.css"', index_html)
			self.assertIn('href="/GodsDev/magic/"', index_html)
			self.assertIn('href="/GodsDev/info/"', index_html)
			self.assertNotIn('nav-link-label">Blog</span>', index_html)
			self.assertIn('id="blog"', index_html)

			info_html = (output_dir / 'info' / 'index.html').read_text(encoding='utf-8')
			self.assertIn('href="/GodsDev/#blog">Visit the blog</a>', info_html)

			magic_html = (output_dir / 'magic' / 'index.html').read_text(encoding='utf-8')
			self.assertIn('data-static-mode="true"', magic_html)
			self.assertIn('/GodsDev/static/home/magic.js', magic_html)
			self.assertNotIn('csrfmiddlewaretoken', magic_html)
