To start development
1. Clone the repo and cd in to the folder (if not in development branch)
2. Activate environment
3. If you are on linux run `export DJANGO_ENVIRONMENT='development'` or if you are on windows run `$env:DJANGO_ENVIRONMENT='development'`
4. do `pip install -r requirements.txt`
5. do `python3 manage.py migrate`
6. do `python3 manage.py runserver`

To release
1. Install flyctl (look at fly.io for instructions)
2. Do `flyctl auth login`
3. Login using browser
4. Run command `flyctl deploy` from the project directory

To set environment variables
1. Run 'flyctl secrets set $environ_variable="environ_variable_value"'

Example: set "STRIPE_WEBHOOK_SECRET"
Run 'flyctl secrets set STRIPE_WEBHOOK_SECRET="whsec_Y1IkdkL1IsP3dggfwpLMsFIOtx7dxMxC"'


github clonnig and run at localhost
1. copy git repository link from github, that is look like `https://github.com/ak21688/hummingbird5.git`
2. run command on your terminal `git clone 'https://github.com/ak21688/hummingbird5.git'`
4. ENTER INTO new create directory `cd hummingbird5`
3. run command on your terminal `git checkout development`
4. run command on your terminal `git pull`

for make any change in github source from current dir:
1. do `git add .`
2. do `git commit -m 'Any message'`
3. do `git push`



