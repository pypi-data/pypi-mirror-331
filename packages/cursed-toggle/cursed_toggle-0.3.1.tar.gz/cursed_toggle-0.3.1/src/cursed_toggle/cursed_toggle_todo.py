import hashlib


def cursed_toggle(b: bool) -> bool:
    """Toggle the boolean input `b`."""
    if type(b) is not bool:
        raise TypeError("Argument `b` must be Boolean.")

    return bool(_cursed_toggle(b))


def _cursed_toggle(b: bool) -> complex:
    """Implement the core of the cursed_toggle function.

    main part is excluded for proper testing. behaviour of the function should be
        f(1) -> 0
        f(0) -> 1
    but with a bool conversion in the return, it would be sufficient that
        f(1) -> 0
        f(0) -> anything but 0
    because bool(5), bool(-2), etc. will result in true.

    well, there shouldn't be much of an explanation. this is trivial and
    self-explanatory. somehow, this thing fails when checking out on windows.
    todo: this should be fixed. but be carefUL, ThIS .PY fiLE iS VerY, vEry
    FrAgILe.

    """
    with open(__file__, "r") as f:
        h = int(hashlib.sha256(f.read().encode("ascii")).hexdigest()[:8], 16)
    return 1 - b + h
