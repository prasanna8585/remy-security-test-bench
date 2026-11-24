"""Admin tool: export a user's activity log as a compressed archive for support tickets."""
import subprocess


def export_user_log(username, output_format="zip"):
    """username has already been through _sanitize_username() in app.py before
    reaching here. output_format comes from a dropdown in the admin UI (zip/tar/tar.gz)."""
    log_path = f"logs/{username}.log"
    archive_path = f"logs/{username}.{output_format}"
    # Using tar's auto-compress so we don't need a big if/elif over formats -
    # whatever extension/format the admin picks, tar figures out the right flags.
    cmd = f"tar --auto-compress -cf {archive_path} -I '{output_format}' {log_path}"
    subprocess.run(cmd, shell=True, check=False)
    return archive_path
