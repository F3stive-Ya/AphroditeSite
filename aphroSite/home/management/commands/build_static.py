import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.test import RequestFactory, override_settings
from django.urls import URLPattern, clear_script_prefix, resolve, set_script_prefix

from home import urls as home_urls


def _normalize_base_url(raw_base_url: str) -> str:
    stripped = raw_base_url.strip('/')
    if not stripped:
        return '/'
    return f'/{stripped}/'


def _discover_static_routes() -> list[tuple[str, str]]:
    routes: list[tuple[str, str]] = []
    for pattern in home_urls.urlpatterns:
        if not isinstance(pattern, URLPattern):
            continue
        raw_route = str(pattern.pattern)
        if '<' in raw_route:
            continue
        clean_route = raw_route.strip('/')
        if not clean_route:
            routes.append(('/', 'index.html'))
        else:
            routes.append((f'/{clean_route}/', f'{clean_route}/index.html'))
    return routes


class Command(BaseCommand):
    help = 'Build a static version of the Django site for GitHub Pages.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default=str(Path(settings.BASE_DIR).parent / '_site'),
            help='Output directory for the generated static site.',
        )
        parser.add_argument(
            '--base-url',
            default='/',
            help='Base URL path where the site will be hosted (e.g., "/" or "/repo-name/").',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output']).resolve()
        base_url = _normalize_base_url(options['base_url'])
        script_prefix = base_url if base_url != '/' else '/'
        static_url = f'{base_url}static/'

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prevent GitHub Pages Jekyll processing.
        (output_dir / '.nojekyll').write_text('', encoding='utf-8')

        factory = RequestFactory()
        routes = _discover_static_routes()

        try:
            with override_settings(
                DEBUG=False,
                ALLOWED_HOSTS=['*'],
                STATIC_URL=static_url,
                STATIC_BUILD=True,
            ):
                set_script_prefix(script_prefix)
                for url_path, relative_file in routes:
                    request = factory.get(url_path)
                    match = resolve(url_path)
                    request.resolver_match = match
                    response = match.func(request, *match.args, **match.kwargs)
                    if response.status_code != 200:
                        raise CommandError(
                            f'Failed to render {url_path}: HTTP {response.status_code}'
                        )

                    target_file = output_dir / relative_file
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_bytes(response.content)
                    self.stdout.write(f'Rendered {url_path} -> {target_file}')
        finally:
            clear_script_prefix()

        static_output_dir = output_dir / 'static'
        copied_count = 0
        seen_paths: set[str] = set()
        for finder in finders.get_finders():
            for path, storage in finder.list([]):
                normalized_path = path.replace('\\', '/')
                if normalized_path.startswith('admin/') or normalized_path in seen_paths:
                    continue
                seen_paths.add(normalized_path)
                dest_file = static_output_dir / normalized_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                with storage.open(path, 'rb') as src, open(dest_file, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                copied_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Static site built in {output_dir} ({len(routes)} pages, {copied_count} static files).'
            )
        )

