from django.conf import settings
from django.shortcuts import render
from .cipher import GREEK_GLYPHS, SECRET_KEY, encrypt_true_thoughts
from .forms import GirdleForm

def index(request):
    profile = {
        'name': 'Aphrodite (\u1f08\u03c6\u03c1\u03bf\u03b4\u03af\u03c4\u03b7)',
        'handle': '@aphroditebythesea',
        'location': 'The Aegean Sea',
        'mood': 'sea-born and sovereign',
        'tagline': 'Goddess of love, desire, and beauty',
        'headline': 'The force that draws the world together.',
        'about': 'Born from sea foam, I embody more than romance. My power is attraction: the pull that reshapes loyalties, choices, and the course of a myth.',
        'origin': 'Born from sea foam',
        'sphere': 'Love, desire, beauty',
        'domains': [
            {'name': 'Desire', 'description': 'The spark that draws hearts, minds, and stories together.'},
            {'name': 'Beauty', 'description': 'A force that commands attention and changes what the world values.'},
            {'name': 'Union', 'description': 'The bonds, vows, and loyalties that shape what comes next.'},
        ],
        'symbols': [
            'Rose',
            'Dove',
            'Myrtle',
            'Seashell',
        ],
        'power_description': 'Come see how my magic girdle can effect the true thoughts of any mortal!',
        'friends': [
            {'name': 'Eros', 'note': 'the spark', 'initials': 'ER'},
            {'name': 'Psyche', 'note': 'love made mortal', 'initials': 'PS'},
            {'name': 'The Muses', 'note': 'keepers of inspiration', 'initials': 'MU'},
            {'name': 'The Graces', 'note': 'beauty in motion', 'initials': 'GR'},
        ],
        'comments': [
            {
                'name': 'Anchises',
                'time': '27 minutes ago',
                'message': 'Despite the consquences, I still desire you.',
                'initials': 'AS',
            },
            {
                'name': 'Eros',
                'time': '2 hours ago',
                'message': 'Found the prettiest shell for your collection Mom. Saving it for you!',
                'initials': 'ER',
            },
            {
                'name': 'Ares',
                'time': '2 weeks ago',
                'message': 'That spear was so heavy! Im still sore!',
                'initials': 'AS',
            },
        ],
        'posts': [
            {
                'category': 'FROM THE TEMPLE',
                'title': 'The most beautiful woman!',
                'body': 'Last night after I had finished bathing, I caught a glimpse of the most beautiful woman! After closer inspection, it turned out to be a mirror.',
                'liked_by': ['Eros', 'Psyche', 'Aphrodite'],
            },
            {
                'category': 'NEW PRAYERS',
                'title': 'Prayers from Lesbos',
                'body': 'Ive been receiving prayer requests from Lesbos lately. Some poet named Sappho pleading for my help in her romantic life. Still undecided to help.',
                'liked_by': ['The Muses', 'The Graces', 'Eros'],
            },
            {
                'category': 'A LAUGH FROM MY LIFE',
                'title': 'A funny trick from my son',
                'body': 'Earlier, Ares was trying to impress me. Eros gave him a spear to hold, and he could barely lift it!',
                'liked_by':['Eros','Psyche','Zeus'],
            }
        ],
    }
    return render(request, 'home/index.html', {'profile': profile})


def magic(request):
    form = GirdleForm(request.POST or None)
    result = None
    cipher_unavailable = False
    submitted_thoughts = None

    if request.method == 'POST' and form.is_valid():
        submitted_thoughts = form.cleaned_data['thoughts']
        try:
            result = encrypt_true_thoughts(submitted_thoughts)
        except NotImplementedError:
            cipher_unavailable = True

    static_build = getattr(settings, 'STATIC_BUILD', False)
    context = {
        'form': form,
        'result': result,
        'cipher_unavailable': cipher_unavailable,
        'submitted_thoughts': submitted_thoughts,
        'static_build': static_build,
    }
    if static_build:
        context['cipher_config'] = {
            'secretKey': SECRET_KEY,
            'greekGlyphs': ''.join(GREEK_GLYPHS),
        }

    return render(request, 'home/magic.html', context)


def info(request):
    return render(request, 'home/info.html')
