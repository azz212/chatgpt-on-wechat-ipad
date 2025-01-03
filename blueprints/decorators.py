from functools import wraps
from quart import session, redirect, url_for

def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return await f(*args, **kwargs)
    return decorated_function 