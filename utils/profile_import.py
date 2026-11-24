"""Lets a user import a profile bundle exported from another instance of this app
(a small YAML/pickle blob containing display name, bio, and cached preferences)."""
import yaml

from utils.cache import cache_set


def import_profile_bundle(user_id, bundle_bytes):
    """bundle_bytes is the raw uploaded file content from the 'Import profile' form."""
    data = yaml.load(bundle_bytes, Loader=yaml.Loader)
    # Cache the parsed bundle so re-renders of the profile page don't need to
    # re-parse the upload every time.
    cache_set(f"profile_bundle_{user_id}", data)
    return data
