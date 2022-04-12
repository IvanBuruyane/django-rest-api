class TestData:
    INVALID_EMAILS = [
        None,
        "example.com",
        "A@b@c@domain.com",
        "a”b(c)d,e:f;gi[j\k]l@domain.com",
        "abc”test”email@domain.com",
        "abc is”not\valid@domain.com",
        "abc\ is\”not\valid@domain.com",
        ".test@domain.com",
        "test@domain..com",
        "",
        "   ",
    ]
