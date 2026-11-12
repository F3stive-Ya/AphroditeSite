from django.conf import settings
from django.shortcuts import render
from .cipher import GREEK_GLYPHS, SECRET_KEY, encrypt_true_thoughts
from .forms import GirdleForm

def index(request):
    profile = {
        'name': 'Aphrodite',
        'handle': '@aphroditebythesea',
        'location': 'The Aegean Sea',
        'mood': 'sea-born and sovereign',
        'tagline': 'Goddess of love, desire, and beauty',
        'headline': 'The force that draws the world together.',
        'about': 'Born from sea foam, Aphrodite embodies more than romance. Her power is attraction: the pull that reshapes loyalties, choices, and the course of a myth. The myth says that she was born by Cyprus, emerging from sea foam created by her Fathers genitals.',
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
        'power_description': 'Come see how Aphrodites magic gilder can hide the true thoughts of any mortal!',
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
                'message': 'Found the prettiest shell for your collection. Saving it for you!',
                'initials': 'ER',
            },
            {
                'name': 'Ares',
                'time': '2 weeks ago',
                'message': 'That spear was so heavy! Im still sore!',
                'initials': 'AS',
            },
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
