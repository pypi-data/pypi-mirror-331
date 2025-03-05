import functools

import structlog
from blinker import signal
from flask import abort
from flask import flash
from flask import redirect
from flask import request
from flask import typing
from flask_login import LoginManager
from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.wrappers import Request

from .models import AnonymousUser
from .models import User
from .utils import url_for_next
from basingse import svcs

IntoResponse = typing.ResponseReturnValue

log = structlog.get_logger(__name__)
request_load = signal("request-load")


def load_auth(token: str) -> User | None:
    """Loads an Authentication from the DB for use with flask-login

    If the auth doesn't exist, flask-login will transparently
    handle issues
    """
    session = svcs.get(Session)
    log.debug("Loading user", token=token)
    return session.execute(select(User).where(User.token == token).limit(1)).scalar_one_or_none()


def request_loader(request: Request) -> User | None:
    """Loads an Authentication from the DB for use with flask-login

    If the auth doesn't exist, flask-login will transparently
    handle issues
    """
    callbacks = request_load.send(request)
    for _, user in callbacks:
        if user is not None:
            return user

    token = request.headers.get("Authorization", None)
    if token is None:
        return None
    return load_auth(token.removeprefix("Bearer "))


def unauthorized(manager: LoginManager) -> IntoResponse:
    """Redirects to the login page, with a flash message if configured"""

    if request.blueprint in manager.blueprint_login_views:
        login_view = manager.blueprint_login_views[request.blueprint]
    else:
        login_view = manager.login_view

    if not login_view:
        abort(401)

    if manager.login_message:
        flash(manager.login_message, category=manager.login_message_category)

    redirect_url = url_for_next(login_view, next=request.url)

    return redirect(redirect_url)


def init_extension(manager: LoginManager) -> None:
    """Set up flask-login once the extension is ready."""
    manager.anonymous_user = AnonymousUser
    manager.unauthorized_handler(functools.partial(unauthorized, manager=manager))
    manager.user_loader(load_auth)
    manager.request_loader(request_loader)
