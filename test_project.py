from project import matchup_str_format, strip_ansi_codes, get_win_char, ONE_MATCH_STR, CORRECT_STR, OVERSHOT_MATCH_STR, NO_MATCH_STR, get_monotype_relation

def test_matchup_str_format():
    assert matchup_str_format(0.5) == "1/2x"
    assert matchup_str_format(0.25) == "1/4x"
    assert matchup_str_format(1) == "1x"
    assert matchup_str_format(2) == "2x"
    assert matchup_str_format(4) == "4x"


def test_strip_ansi_codes():
    assert strip_ansi_codes("\033[1mHello\033[0m") == "Hello"
    assert strip_ansi_codes("\033[1mHello\033[0m world") == "Hello world"
    assert strip_ansi_codes("Hello world") == "Hello world"


def test_get_win_char():
    assert get_win_char(["normal"], ["fighting", "fire"]) == NO_MATCH_STR
    assert get_win_char(["fire", "psychic"], ["ghost", "fire"]) == ONE_MATCH_STR
    assert get_win_char(["fire", "flying"], ["flying"]) == OVERSHOT_MATCH_STR
    assert get_win_char(["poison"], ["poison"]) == CORRECT_STR


def test_get_monotype_relation():
    assert get_monotype_relation("poison", "steel") == 0
    assert get_monotype_relation("poison", "grass") == 2
    assert get_monotype_relation("poison", "normal") == 1
    assert get_monotype_relation("fighting", "flying") == 0.5
