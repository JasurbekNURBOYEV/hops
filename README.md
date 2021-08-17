<img src="https://telegra.ph/file/1fd7625b0cb6cbbe23be4.jpg" alt="Hops" title="Hops" width="150" height="150" />

# Hops 2.1
    v2.2 is under development (which brings early pieces of Greed Island & FlashOverflow)

*An officer robot for Python UZBEKISTAN Community.*

**Made of Python & Made for Python**

Home page: [hops.nurboyev.uz](https://hops.nurboyev.uz)

### How to run

- Install docker & docker-compose
- create `.env` file in root project directory
- add these values to `.env`:
  - `BOT_TOKEN` - token of YOUR bot
  - `MAIN_GROUP_ID` - chat id of your main Telegram group
  - `TEST_GROUP_ID` - chat id of your test group
  - `BOARD_GROUP_ID` - chat id of group for management
  - `DEV_ID` - ID of YOUR Telegram account
  - `TELEGRAPH_TOKEN` - Telegraph token
  - `SECRET_KEY` - secret key of django project
  - `HOSTS` - allowed hosts
  - `CONTROL_PAGE_URL` - url name for admin panel, e.g: `admin/`
  - `DOMAIN_URL` - main domain URL with schema included, e.g: `http://hops.nurboyev.uz` or `http://127.0.0.1:1243` for local development
  - `PROD` - leave empty for DEBUG mode, give anything to enable production mode & disable DEBUG
- run `docker-compose up -d --build`
- run `docker-compose exec core python manage.py collectstatic`
- run `docker-compose exec core python manage.py makemigrations`
- run `docker-compose exec core python manage.py migrate`
- run `docker-compose exec core python manage.py createsuperuser`
- you may need <a href="https://ngrok.com">ngrok</a> to run bot locally, it helps you expose your local machine to internet, so you can use webhook locally.
- God bless you and may give you great patience

### Download the repo, play with it, check for bugs, try to improve.