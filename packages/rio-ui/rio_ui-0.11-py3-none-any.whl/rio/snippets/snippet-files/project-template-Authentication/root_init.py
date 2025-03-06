# <additional-imports>
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import rio

from . import data_models, persistence, theme

# </additional-imports>


# <additional-code>
async def on_app_start(app: rio.App) -> None:
    # Create a persistence instance. This class hides the gritty details of
    # database interaction from the app.
    pers = persistence.Persistence()

    # Now attach it to the session. This way, the persistence instance is
    # available to all components using `self.session[persistence.Persistence]`
    app.default_attachments.append(pers)


async def on_session_start(rio_session: rio.Session) -> None:
    # A new user has just connected. Check if they have a valid auth token.
    #
    # Any classes inheriting from `rio.UserSettings` will be automatically
    # stored on the client's device when attached to the session. Thus, by
    # retrieving the value here, we can check if the user has a valid auth token
    # stored.
    user_settings = rio_session[data_models.UserSettings]

    # Get the persistence instance
    pers = rio_session[persistence.Persistence]

    # Try to find a session with the given auth token
    try:
        user_session = await pers.get_session_by_auth_token(
            user_settings.auth_token,
        )

    # None was found - this auth token is invalid
    except KeyError:
        pass

    # A session was found. Welcome back!
    else:
        # Make sure the session is still valid
        if user_session.valid_until > datetime.now(tz=timezone.utc):
            # Attach the session. This way any component that wishes to access
            # information about the user can do so.
            rio_session.attach(user_session)

            # For a user to be considered logged in, a `UserInfo` also needs to
            # be attached.
            userinfo = await pers.get_user_by_id(user_session.user_id)
            rio_session.attach(userinfo)

            # Since this session has only just been used, let's extend its
            # duration. This way users don't get logged out as long as they keep
            # using the app.
            await pers.update_session_duration(
                user_session,
                new_valid_until=datetime.now(tz=timezone.utc)
                + timedelta(days=7),
            )


# </additional-code>


# Make sure ruff doesn't remove unused imports
# Create the Rio app
app = rio.App(
    name="Authentication",
    theme=theme.THEME,
)
