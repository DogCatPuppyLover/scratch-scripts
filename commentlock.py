import requests
from time import sleep
from getpass import getpass

def prepare_session(username: str, password: str) -> requests.Session:
    # Reference: https://github.com/yuwex/scratchcloud/blob/main/scratchcloud/client.py#L362

    # Cookie header isn't needed
    headers = {
        "X-CSRFToken": "None",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://scratch.mit.edu",
        "User-Agent": "commentlock",
    }

    # Create session
    session = requests.Session()
    session.headers = headers

    # Get CSRF first instead of making one up. This is a best practice.
    resp = session.get("https://scratch.mit.edu/csrf_token/", headers=headers)

    # Use built in resp.cookies.get() instead of regex.
    csrf_token = resp.cookies.get("scratchcsrftoken")

    # Update headers to include real CSRF
    session.headers["X-CSRFToken"] = csrf_token

    # Prepare login payload
    payload = {
        "username": username,
        "password": password,
    }

    # Log in with CSRF Token.
    resp = session.post(
        "https://scratch.mit.edu/login/",
        json=payload,
    )

    # Update headers to include auth token.
    token = resp.json()[0]["token"]
    session.headers["X-Token"] = token

    code = resp.status_code

    if code == 200:
        return session
    else:
        raise ConnectionError(
            f"Got status code {code}. Maybe you entered invalid login information?"
        )

def set_comments_allowed(
    session: requests.Session,
    username: str,
    comments_allowed: bool,
    cooldown: float = 0.1,
):

    offset = 0
    projects = []

    # Set up payload only once
    payload = {"comments_allowed": comments_allowed}

    while len(projects) == 20 or offset == 0:

        # Use python integer division and f-strings to condense
        print(f"Page: {offset // 20 + 1}")

        # Use response.json() to get data immediately
        projects = session.get(
            f"https://api.scratch.mit.edu/users/{username}/projects/?offset={offset}"
        ).json()

        for project in projects:
            # More f-strings :)
            resp = session.put(
                f"https://api.scratch.mit.edu/projects/{project['id']}/", json=payload
            )

            # Print out project title as well as id with some nice formatting.
            success_text = (
                "Success!"
                if resp.status_code == 200
                else f"Failed with code {resp.status_code}"
            )
            print(f"   {project['title']} [{project['id']}] - {success_text}")

            # Use sleep to prevent ratelimiting / bans :D
            sleep(cooldown)

        offset += 20


# Use __name__ == '__main__' to prevent accidental running
if __name__ == "__main__":

    print("Welcome to the commentlock tool!")

    username = input("Enter your username: ")
    password = getpass("Enter your password: ")

    # Make comments_on variable into 1-line
    comments_on = input("Should comments be enabled? Y/n: ").lower() == "y"

    # Add cooldown
    cooldown = float(
        input("How long should the request cooldown be? (0.1 recommended): ")
    )

    print("\n")

    print("Logging in...")

    # Use functions to break up code
    session = prepare_session(username, password)

    print("Setting project status...")

    set_comments_allowed(session, username, comments_on, cooldown)

    session.close()
