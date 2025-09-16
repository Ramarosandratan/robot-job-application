import asyncio

async def is_duplicate_application(client, job_id: int, user_id: int) -> bool:
    """
    Checks the `applications` table to see if an application for the given `job_id`
    by the `user_id` already exists.

    Args:
        client: The Supabase client.
        job_id (int): The ID of the job.
        user_id (int): The ID of the user.

    Returns:
        bool: True if a duplicate application is found, False otherwise.
    """
    response = await client.from_('applications').select('*').eq('job_id', job_id).eq('user_id', user_id).execute()
    if response.data:
        return True
    return False