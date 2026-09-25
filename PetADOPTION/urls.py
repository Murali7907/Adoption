from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from users.views import profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hero.mp4', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'hero.mp4'}),
    path('pet_hero.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'pet_hero.jpg'}),
    path('pet_login.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'pet_login.jpg'}),
    path('featured_dog.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'featured_dog.jpg'}),
    path('featured_cat.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'featured_cat.jpg'}),
    path('kindheart_family.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_family.jpg'}),
    path('kindheart_bruno.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_bruno.jpg'}),
    path('luna_siamese.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'luna_siamese.jpg'}),
    path('rocky_shepherd.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'rocky_shepherd.jpg'}),
    path('coco_beagle.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'coco_beagle.jpg'}),
    path('kindheart_elephant.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_elephant.jpg'}),
    path('kindheart_real_hero.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_real_hero.jpg'}),
    path('kindheart_journey.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_journey.jpg'}),
    path('kindheart_real_shelter.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_real_shelter.jpg'}),
    path('kindheart_3d_retriever.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_3d_retriever.jpg'}),
    path('kindheart_3d_model_retriever.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_3d_model_retriever.jpg'}),
    path('kindheart_3d_model_cat.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_3d_model_cat.jpg'}),
    path('kindheart_3d_elephant.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_3d_elephant.jpg'}),
    path('kindheart_real_elephant.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_real_elephant.jpg'}),
    path('kindheart_elephant_walking_side.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'kindheart_elephant_walking_side.jpg'}),
    path('about_us_bg.mp4', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'about_us_bg.mp4'}),
    path('contact_shelter_help.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'contact_shelter_help.jpg'}),
    path('contact_sanctuary_help.jpg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'contact_sanctuary_help.jpg'}),
    path('styles.css', serve, {'document_root': settings.BASE_DIR, 'path': 'styles.css'}),
    path('script.js', serve, {'document_root': settings.BASE_DIR, 'path': 'script.js'}),
    path('shelter_store.js', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'shelter_store.js'}),
    path('relaxing_birds.wav', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'relaxing_birds.wav'}),
    path('favicon.svg', serve, {'document_root': settings.BASE_DIR / 'public', 'path': 'favicon.svg'}),
    re_path(r'^(?P<path>.*\.(?:jpg|jpeg|png|gif|svg|mp4|webm|wav|mp3|ogg|glb|gltf|bin|js))$', serve, {'document_root': settings.BASE_DIR / 'public'}),
    path('', include('pets.urls')),
    path('users/', include('users.urls')),
    path('profile/', profile_view, name='direct_profile'),
    path('dashboard/', profile_view, name='direct_dashboard'),
]








