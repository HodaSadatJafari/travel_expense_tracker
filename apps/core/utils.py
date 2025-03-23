from django.contrib.auth.models import User


def get_or_create_user(first_name=None, last_name=None, email=None):
    """
    Get an existing user or create a new one based on available information
    Returns a tuple (user, created) where created is a boolean
    """
    # If email is provided, try to find existing user by email
    if email:
        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            pass  # Continue with user creation

    # Generate base username
    if first_name and last_name:
        base_username = f"{first_name.lower()}_{last_name.lower()}"
    elif first_name:
        base_username = first_name.lower()
    elif last_name:
        base_username = last_name.lower()
    else:
        # Generate random username if no name info provided
        import uuid

        base_username = f"traveler_{uuid.uuid4().hex[:8]}"

    # Ensure username is unique
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1

    # Generate a random password
    import uuid

    temp_password = str(uuid.uuid4())[:8]

    # Create a placeholder email if none provided
    if not email:
        email = f"{username}@placeholder.traveler"

    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=temp_password,  # User should reset this
        first_name=first_name or "",
        last_name=last_name or "",
    )

    return user, True
