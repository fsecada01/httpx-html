"""Utility functions for httpx-html."""

from typing import Union, Optional


def get_first_or_list(lst: list, first: bool = False) -> Union[list, Optional[object]]:
    """Return either the first item or the full list based on the first parameter.
    
    Args:
        lst: List to process
        first: If True, return first item; if False, return full list
        
    Returns:
        First item if first=True, full list if first=False, None if empty and first=True
    """
    if first:
        try:
            return lst[0]
        except IndexError:
            return None
    else:
        return lst