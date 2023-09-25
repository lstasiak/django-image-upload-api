# django-image-upload-api

Web api developed in django and django-rest-framework
to upload images and generate thumbnails depending on user profile subscription.

Built-in subscriptions available in the app (created via data migration file):
- `Basic`:
  - generates thumbnail with size: width x 200px
- `Premium`:
  - generates thumbnail with size: width x 200px
  - generates thumbnail with size: width x 400px
  - generates link to original image file
- `Enterprise`:
  - generates thumbnail with size: width x 200px
  - generates thumbnail with size: width x 400px
  - generates link to original image file
  - generates special link (with signature) with specific expiration time to download original image

By default `width` size parameter is calculated automatically as `height*aspect_ratio`, where `aspect_ratio = 16/9`
but can be defined when creating thumbnail size object.

For the test purposes, admin superuser is created automatically with the start of the app server.

## Local setup
Inside project directory:
1. Build image and start: `docker-compose -up --build`
2. Go to admin site: `http://0.0.0.0:8000/admin/` and login as test admin (to provide authentication):\
`Username: admin` \
`Password: admin`
3. Test admin has "Basic" subscription, so in case to test the other types, edit subscription field in admin Profile site.
4. Go to image api site: `http://0.0.0.0:8000/api/images/` and using REST UI add new image providing file and title.
5. Check if image is listed and if `img_urls` list has expected thumbnail links.
6. Additionally, created images/thumbnails are stored locally in `/media/` directory.
7. To generate expiring link, e.g. for "Enterprise" subscription, got to http://0.0.0.0:8000/api/expiring-links/ and create one for selected (previously uploaded) image.
8. Check if `img_urls` field in `/api/images/` contains expiring link (assuming the subscription allows it)

## Additional functionalities
1. We can run django tests using make command:
```make test```
*Additional Comment: Two test functions were commented due to problems with mocking function get_thumbnails called in serializer, but I thought to leave them, to show the general idea.
2. To perform code formatting/linting using black, isort and ruff we can run:
```make perform .```
