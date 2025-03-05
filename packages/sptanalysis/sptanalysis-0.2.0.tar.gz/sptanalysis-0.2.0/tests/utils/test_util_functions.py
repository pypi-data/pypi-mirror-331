from sptanalysis.utils.util_functions import dic_union_two


def test_dic_union_two():
    a = dic_union_two({"hi": []}, {"world": []})
    assert a == {"hi": [], "world": []}
