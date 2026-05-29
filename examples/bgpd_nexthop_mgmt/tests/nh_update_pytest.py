from bgpd_nexthop_mgmt.api_bgp_nh_update import BgpdRouteEvent, DownstreamMsgs
from bgpd_nexthop_mgmt.api_bgp_nh_update import BOp
from bgpd_nexthop_mgmt.crosshair_target import api_bgp_nh_update_with_precondition

def test_api_bgp_nh_update_with_precondition():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [], 2, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[2])])

def test_api_bgp_nh_update_with_precondition_2():
    assert api_bgp_nh_update_with_precondition([], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_3():
    assert api_bgp_nh_update_with_precondition([(0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_4():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [], 2, 2, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[2])])

def test_api_bgp_nh_update_with_precondition_5():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [], 2, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_6():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [], 2, 2, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_7():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [], 2, 3, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_8():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_9():
    assert api_bgp_nh_update_with_precondition([(0, [3, 4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_10():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_11():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_12():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_13():
    assert api_bgp_nh_update_with_precondition([(0, [4, 3])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_14():
    assert api_bgp_nh_update_with_precondition([(0, [3, 4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_15():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_16():
    assert api_bgp_nh_update_with_precondition([(0, [4, 4, 4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_17():
    assert api_bgp_nh_update_with_precondition([(0, [4, 4, 4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_18():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_19():
    assert api_bgp_nh_update_with_precondition([(0, [4, 4, 4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_20():
    assert api_bgp_nh_update_with_precondition([(0, [4, 5, 4])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_21():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3]), v1], [], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_22():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4]), v1], [], 3, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_23():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3]), v1], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_24():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_25():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_26():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_27():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_28():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_29():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_30():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3]), v1], [], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_31():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3]), v1], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_32():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_33():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_34():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [], 3, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_35():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [0])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_36():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_37():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_38():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_39():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5]), BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_40():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [5])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_41():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [0])], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_42():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [0])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_43():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=3, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_44():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4, 3]), v1], [], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_45():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3, 3]), v1], [], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_46():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_47():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_48():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_49():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_50():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_51():
    assert api_bgp_nh_update_with_precondition([(6, [4, 3]), (5, [])], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_52():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_53():
    assert api_bgp_nh_update_with_precondition([(4, [3, 3]), (4, [])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_54():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_55():
    assert api_bgp_nh_update_with_precondition([(5, [3, 6]), (4, [])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_56():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_57():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3, 3]), v1], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_58():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3, 3]), v1], [], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_59():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3, 4]), v1], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_60():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_61():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[3]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_62():
    assert api_bgp_nh_update_with_precondition([(5, [6, 3]), (4, [3])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_63():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[3]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_64():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [(2, 0, False)], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_65():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5, 5])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5]), BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_66():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [(2, 0, False)], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_67():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [(2, 0, True)], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_68():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 3, False)], 2, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[2])])

def test_api_bgp_nh_update_with_precondition_69():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_70():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 3, False)], 2, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[2])])

def test_api_bgp_nh_update_with_precondition_71():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_72():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_73():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_74():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_75():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5, 5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5]), BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_76():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_77():
    assert api_bgp_nh_update_with_precondition([(5, [3, 6]), (4, [])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_78():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_79():
    assert api_bgp_nh_update_with_precondition([(4, [7]), (3, [6, 5])], [], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_80():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_81():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [0, 0])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=3, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_82():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 0, False)], 3, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_83():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [(2, 0, False)], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_84():
    assert api_bgp_nh_update_with_precondition([(0, [3])], [(2, 0, False)], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_85():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 3, False)], 2, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_86():
    assert api_bgp_nh_update_with_precondition([(5, [3, 6]), (4, [3])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_87():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 3, False)], 2, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_88():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_89():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5, 5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=3, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_90():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_91():
    assert api_bgp_nh_update_with_precondition([(4, [3, 3]), (4, [0])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_92():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5, 5])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_93():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5, 4, 4])], [], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_94():
    assert api_bgp_nh_update_with_precondition([(6, [4, 4, 4]), (5, [])], [], 4, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_95():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 4, 4])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_96():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False)], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_97():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_98():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False)], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_99():
    assert api_bgp_nh_update_with_precondition([(0, [4, 3])], [(5, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_100():
    assert api_bgp_nh_update_with_precondition([(0, [3, 5])], [(4, 0, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_101():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(3, 4, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_102():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_103():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_104():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [], 4, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_105():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3, 6])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_106():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_107():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_108():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, [4]), v1], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_109():
    assert api_bgp_nh_update_with_precondition([v1:=(4, []), (5, [6]), v1], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_110():
    assert api_bgp_nh_update_with_precondition([v1:=(5, [6]), v1, (4, [])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_111():
    assert api_bgp_nh_update_with_precondition([v1:=(4, []), (4, [5]), v1], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_112():
    assert api_bgp_nh_update_with_precondition([v1:=(4, []), (5, [7]), v1], [], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_113():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False)], 3, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_114():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_115():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False)], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_116():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, [4]), v1], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_117():
    assert api_bgp_nh_update_with_precondition([(5, [6]), v1:=(4, []), v1], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_118():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_119():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_120():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, []), (6, [])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_121():
    assert api_bgp_nh_update_with_precondition([v1:=(5, [7]), v1, (4, [])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_122():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_123():
    assert api_bgp_nh_update_with_precondition([(5, [6]), v1:=(4, [6]), v1], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_124():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [6]), (4, [])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_125():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (4, []), (5, [])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_126():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_127():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [6]), (4, [])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_128():
    assert api_bgp_nh_update_with_precondition([(7, [5, 5, 5, 6]), (7, [])], [], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_129():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, [5]), v1], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_130():
    assert api_bgp_nh_update_with_precondition([(5, [6]), (4, []), (5, [])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_131():
    assert api_bgp_nh_update_with_precondition([(5, [6]), v1:=(4, [6]), v1], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_132():
    assert api_bgp_nh_update_with_precondition([v1:=(5, [6]), v1, (4, [])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_133():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5, 5, 5, 5])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_134():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [5, 5, 5, 5]), v1], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_135():
    assert api_bgp_nh_update_with_precondition([(5, [7]), v1:=(4, []), v1], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_136():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [6]), (4, [])], [], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_137():
    assert api_bgp_nh_update_with_precondition([(0, []), (4, [5]), (4, [0])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_138():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_139():
    assert api_bgp_nh_update_with_precondition([(5, [6]), v1:=(4, [6]), v1], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_140():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [7]), (4, [])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_141():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_142():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_143():
    assert api_bgp_nh_update_with_precondition([(0, []), (4, [5]), (4, [])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_144():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5, 5, 5, 5])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_145():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_146():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, [7]), (6, [])], [], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_147():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_148():
    assert api_bgp_nh_update_with_precondition([(5, [4, 4]), v1:=(5, []), v1], [], 4, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_149():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5, 4])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_150():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4]), v1], [(3, 0, True)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_151():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [6]), (4, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_152():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_153():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, True)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_154():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, True)], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_155():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3]), v1], [(3, 4, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_156():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4])], [], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_157():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_158():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_159():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5, 4])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_160():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_161():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [])], [(4, 0, True)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_162():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_163():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [v1:=(3, 0, False), v1], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_164():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [v1:=(3, 0, False), v1], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_165():
    assert api_bgp_nh_update_with_precondition([(0, []), (6, [4, 4]), (5, [])], [], 4, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_166():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [v1:=(3, 0, False), v1], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_167():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, [7]), (6, [7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_168():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [v1:=(3, 0, True), v1], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_169():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [4, 4]), v1, (5, [])], [], 4, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=6, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_170():
    assert api_bgp_nh_update_with_precondition([(6, [4, 4]), (5, []), (6, [])], [], 4, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_171():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_172():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [7]), (5, []), v1, v1], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_173():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [])], [(4, 0, True)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_174():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4])], [], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_175():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_176():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [4, 4]), v1, (5, [])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_177():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_178():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v1, (6, [7]), v1], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_179():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4]), v1], [(3, 0, True)], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_180():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [4, 7]), v1, (5, [])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=6, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_181():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 4, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_182():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 4, False)], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_183():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 4, True)], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_184():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5])], [(5, 6, True)], 5, 6, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_185():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 6, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_186():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 6, True)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_187():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, [7, 6]), (8, [])], [], 7, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[7]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_188():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v1, (5, [6]), v1], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_189():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, [6])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_190():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 6, False)], 5, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_191():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_192():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [v1:=(3, 0, False), v1], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_193():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4])], [], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_194():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4])], [], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_195():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_196():
    assert api_bgp_nh_update_with_precondition([(6, [4, 4]), (5, []), (7, [])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_197():
    assert api_bgp_nh_update_with_precondition([(0, []), (4, [5]), (4, [0, 0])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_198():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [0])], [(4, 0, True)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_199():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v1, (5, [7]), v1], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_200():
    assert api_bgp_nh_update_with_precondition([(0, []), (6, [4, 4]), (5, [])], [], 4, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=6, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_201():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 0, False)], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_202():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_203():
    assert api_bgp_nh_update_with_precondition([(0, [5, 5, 5, 5])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_204():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False)], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_205():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False)], 4, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_206():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 6, False)], 5, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_207():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4, 4])], [], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_208():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_209():
    assert api_bgp_nh_update_with_precondition([(0, [5, 5, 5, 5])], [(6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_210():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False)], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_211():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 6, False)], 5, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_212():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [0])], [(4, 5, False)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_213():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_214():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False)], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_215():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [])], [(4, 0, False)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=3, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_216():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_217():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [(3, 6, True)], 3, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_218():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [4, 4, 4]), (5, [])], [], 4, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_219():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 5, 4])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_220():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, [5, 5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_221():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5, 4, 5])], [], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_222():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, True)], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_223():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 5, 4])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_224():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_225():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4, 4])], [], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_226():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), (7, [5, 5]), v1, v1], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_227():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_228():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_229():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4, 5])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_230():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_231():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_232():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v2:=(6, [7]), v2, v1], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_233():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, [6, 5])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_234():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5, 4, 6])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_235():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_236():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [(3, 6, False)], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_237():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(3, 4, False)], 3, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_238():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_239():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [(3, 6, True)], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_240():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_241():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [5, 5]), v1, v1, (6, [])], [], 5, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=7, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_242():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(3, 4, True)], 3, 4, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_243():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4, 3]), v1], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_244():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(3, 4, False)], 3, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_245():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [3, 4]), v1], [(4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_246():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [])], [(3, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_247():
    assert api_bgp_nh_update_with_precondition([(0, []), (6, [8]), v1:=(5, []), v1], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_248():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [(4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_249():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_250():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), (5, [7]), v1, (6, [])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_251():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_252():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), (0, []), (6, [7]), v1], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_253():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [5])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_254():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [5])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_255():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_256():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [8]), (5, []), (7, []), v1], [], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_257():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False)], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_258():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_259():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_260():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [6]), (4, [6, 6, 6])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_261():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False)], 3, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_262():
    assert api_bgp_nh_update_with_precondition([(4, [3, 3]), (4, [])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_263():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_264():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_265():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(3, 4, False)], 3, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_266():
    assert api_bgp_nh_update_with_precondition([(5, [3, 3]), (4, [3])], [(3, 6, True)], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_267():
    assert api_bgp_nh_update_with_precondition([(0, []), (6, [7]), v1:=(5, []), v1], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_268():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v2:=(6, [7]), v2, v1], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=6, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_269():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_270():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_271():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6, 5, 5, 7])], [], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_272():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, False), (4, 5, True)], 4, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_273():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [6, 4, 4]), v1], [(5, 0, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_274():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, True), (4, 5, False)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_275():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, True), (5, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_276():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(3, 0, True), (4, 0, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_277():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [5])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_278():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [6])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_279():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_280():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [6])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_281():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4, 4, 4]), v1], [(4, 0, False)], 5, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_282():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_283():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [5])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_284():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_285():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_286():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_287():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_288():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, False), (4, 5, True)], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_289():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(3, 0, False), (4, 0, False)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_290():
    assert api_bgp_nh_update_with_precondition([(0, [2])], [(2, 3, True), (0, 0, False)], 2, 3, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_291():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_292():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, (0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_293():
    assert api_bgp_nh_update_with_precondition([(6, [9]), (5, []), (7, [8, 8, 8, 8])], [], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_294():
    assert api_bgp_nh_update_with_precondition([(6, [10]), (5, []), (7, []), (8, [])], [], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_295():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (5, [7]), (5, [])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_296():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), v2:=(7, [5, 5]), v2, v1], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_297():
    assert api_bgp_nh_update_with_precondition([(0, []), (8, [5, 5, 5, 6]), (7, [])], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_298():
    assert api_bgp_nh_update_with_precondition([v1:=(4, []), (5, [6]), v1], [(6, 0, True)], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_299():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_300():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, False), (4, 5, False)], 4, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_301():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, False), (4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_302():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_303():
    assert api_bgp_nh_update_with_precondition([(0, [4])], [(3, 0, False), (4, 5, False)], 4, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_304():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [6, 5])], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_305():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(3, 0, False), (4, 0, False)], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_306():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(3, 0, False), (4, 0, False)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_307():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_308():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(7, [5, 5]), (6, []), v1], [], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_309():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_310():
    assert api_bgp_nh_update_with_precondition([(5, [9, 7]), (4, []), (6, [7, 9, 7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=6, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_311():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, [5, 5]), v1], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_312():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_313():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_314():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v2:=(0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_315():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_316():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_317():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [(4, 5, True)], 4, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_318():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_319():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_320():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_321():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_322():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_323():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, True)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_324():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_325():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_326():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [9]), v1, v1, v2:=(6, []), v2], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_327():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [v1:=(3, 0, False), v1], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_328():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [v1:=(3, 0, False), v1], 4, 4, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_329():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [v1:=(5, 0, False), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_330():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_331():
    assert api_bgp_nh_update_with_precondition([(5, [8]), (4, []), (6, [])], [(7, 0, True)], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_332():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [5, 5])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_333():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, False)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_334():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, True)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_335():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, True)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_336():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, (0, [7])], [], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_337():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6, 6, 6, 6, 6])], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_338():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), (7, [9]), v1, v1, (7, [])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_339():
    assert api_bgp_nh_update_with_precondition([(0, []), (4, [6]), (4, [])], [(5, 0, True)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_340():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [v1:=(3, 0, False), v1], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_341():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [8]), v1, (6, []), v1, (7, [])], [], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=7, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_342():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, [6])], [], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_343():
    assert api_bgp_nh_update_with_precondition([(0, [3, 5])], [(3, 0, False), (4, 0, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_344():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, True)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_345():
    assert api_bgp_nh_update_with_precondition([v1:=(5, [6]), (4, []), v1], [(6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_346():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_347():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False), (3, 0, True)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_348():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False), (3, 5, False)], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_349():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [6, 5]), v1, (7, []), (9, [5])], [], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_350():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_351():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [(4, 5, False)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_352():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, [7])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_353():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, False)], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_354():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False), (5, 0, False)], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_355():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [v1:=(3, 0, False), v1], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_356():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [v1:=(5, 0, False), v1], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_357():
    assert api_bgp_nh_update_with_precondition([(3, [5]), (3, [])], [v1:=(4, 0, False), v1], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_358():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(6, []), (7, [9]), v1, v1], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_359():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [v1:=(5, 0, False), v1], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_360():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, True), (5, 0, False)], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_361():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4])], [(4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_362():
    assert api_bgp_nh_update_with_precondition([(0, []), (8, [6, 5]), (7, []), (9, [])], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_363():
    assert api_bgp_nh_update_with_precondition([(0, []), (8, [6, 5]), (7, []), (9, [6])], [], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_364():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [7, 5, 6])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_365():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4])], [(4, 0, False)], 5, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_366():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), (0, []), (6, [5, 7, 5]), v1], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_367():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_368():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False)], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_369():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False), (5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_370():
    assert api_bgp_nh_update_with_precondition([(0, [3, 3])], [(4, 0, False), (3, 5, False)], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_371():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_372():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [6, 5, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_373():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_374():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_375():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [6, 5, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_376():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_377():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_378():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_379():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, (0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_380():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_381():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, v1, (0, [7, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_382():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_383():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5, 5, 5])], [], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_384():
    assert api_bgp_nh_update_with_precondition([(6, [7]), (5, [7, 7, 7, 7]), (8, [9, 9])], [], 7, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7]), BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_385():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_386():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_387():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_388():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_389():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_390():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_391():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_392():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_393():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_394():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_395():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_396():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_397():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_398():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_399():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_400():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_401():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, [6, 6])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_402():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_403():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_404():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_405():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_406():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_407():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_408():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_409():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_410():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_411():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_412():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (7, [8]), (6, [])], [], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_413():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_414():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_415():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [6])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_416():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_417():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, False), (5, 0, True), v1], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_418():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(7, [9]), v2, (6, [])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_419():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_420():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [9]), v1, v2:=(6, []), v2, (8, [])], [], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_421():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_422():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, [5])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_423():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_424():
    assert api_bgp_nh_update_with_precondition([(6, [4, 4]), (5, []), (7, [])], [(8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_425():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_426():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(8, []), (7, [10]), (6, []), v1], [], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_427():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, True), (4, 5, False)], 4, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_428():
    assert api_bgp_nh_update_with_precondition([v1:=(7, []), (0, []), v1, v1, (8, [10]), v1], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_429():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_430():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [v1:=(4, 0, True), v1, (6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_431():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_432():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (7, [9]), (6, [])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_433():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, False), (5, 0, True), v1], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_434():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, False), (5, 0, False), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_435():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_436():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [6])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_437():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [7])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_438():
    assert api_bgp_nh_update_with_precondition([(6, [4, 4]), (5, [4]), (7, [])], [(8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_439():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_440():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, False), v1, (5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_441():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, True), v1, (5, 0, False)], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_442():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_443():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_444():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [v1:=(4, 0, False), (6, 0, True), v1], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_445():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [4, 4, 5])], [(6, 0, True)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_446():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [7])], [], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_447():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(3, 0, False), (4, 0, False)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_448():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(3, 0, False), (4, 0, True)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_449():
    assert api_bgp_nh_update_with_precondition([(7, [5, 5]), (6, [8, 8]), (9, []), (10, [])], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_450():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(3, 0, False), (4, 0, True)], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_451():
    assert api_bgp_nh_update_with_precondition([(4, [5]), (3, [5])], [(5, 6, False), (0, 0, True)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=3, nexthops=[5]), BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_452():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(7, []), (7, [8]), (6, [8]), v1], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_453():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(3, 0, False), (4, 0, False)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_454():
    assert api_bgp_nh_update_with_precondition([(7, [9]), (6, []), (7, []), v1:=(8, []), v1], [], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=7, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_455():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [9]), v2:=(6, [9]), v2, v1, (8, [9])], [], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_456():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False), (4, 5, False)], 4, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[4])])

def test_api_bgp_nh_update_with_precondition_457():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), v1, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_458():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False), (4, 5, True)], 4, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_459():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v1, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_460():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_461():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [6])], [], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_462():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5, 4, 4])], [(6, 0, True)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_463():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(4, 0, False), v1:=(6, 0, False), v1], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_464():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(0, [7, 6]), v2], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_465():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [6])], [], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_466():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_467():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 6, 4])], [(5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_468():
    assert api_bgp_nh_update_with_precondition([(4, [7]), (3, [])], [(5, 0, False), (6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_469():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False), (6, 7, False)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_470():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, v2:=(0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_471():
    assert api_bgp_nh_update_with_precondition([(4, [7]), (3, [])], [(5, 0, False), (6, 0, False)], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_472():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(4, 0, False), v1:=(5, 0, False), v1], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_473():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v2, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_474():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(4, 0, False), (5, 0, False), v1], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_475():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), v2, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_476():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, True), (7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_477():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), (7, [9, 6]), v2:=(7, []), v1, v2], [], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_478():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [9, 6]), v2:=(7, [9]), v2, v1, (7, [])], [], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[9]), BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_479():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 4, False), (0, 0, False)], 3, 4, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_480():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False), (5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_481():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), v2:=(6, [8]), v2, v1], [(7, 0, False)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_482():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, []), (6, [8, 7, 8])], [(9, 0, True)], 7, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7]), BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_483():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_484():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(3, 0, False), (4, 5, False)], 4, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_485():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [6, 6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_486():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_487():
    assert api_bgp_nh_update_with_precondition([(7, [11]), (6, []), (8, []), v1:=(9, []), v1], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_488():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, True), (5, 0, True)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_489():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6, 6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_490():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [6, 6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_491():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_492():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_493():
    assert api_bgp_nh_update_with_precondition([(4, [7]), (3, [])], [(5, 0, False), (6, 0, False)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_494():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_495():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_496():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [v1:=(4, 0, True), v1], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_497():
    assert api_bgp_nh_update_with_precondition([(4, [7]), (3, [])], [(5, 0, False), (6, 0, False)], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_498():
    assert api_bgp_nh_update_with_precondition([(0, [4, 4])], [v1:=(5, 0, True), v1, (6, 0, False)], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_499():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [4, 4, 4])], [(5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_500():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_501():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_502():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, v2, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_503():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [])], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_504():
    assert api_bgp_nh_update_with_precondition([v1:=(5, []), (0, []), (6, [7]), v1], [(7, 8, False)], 7, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_505():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), (7, [6, 6]), (7, []), v1, (9, [6])], [], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[6]), BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_506():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_507():
    assert api_bgp_nh_update_with_precondition([v1:=(6, [7]), v2:=(5, [7]), v2, v1], [(7, 8, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[7]), BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_508():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_509():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_510():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, []), (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_511():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), (7, [6, 6]), v2:=(7, [0]), v1, v2], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_512():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, (7, [8]), (7, [])], [], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_513():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_514():
    assert api_bgp_nh_update_with_precondition([v1:=(7, []), (0, []), (0, []), v1, (8, [9]), v1], [], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_515():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, True), (3, 5, False)], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_516():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_517():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, []), (0, [7])], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_518():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_519():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, []), (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_520():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, (0, [7, 6])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_521():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_522():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, False)], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_523():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), (8, [10]), v2:=(7, []), v2, v2, v1], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_524():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_525():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [7, 6, 7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_526():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_527():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, True)], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_528():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [v1:=(4, 0, False), v1], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_529():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [(5, 6, False)], 5, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_530():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, True)], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_531():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_532():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [(5, 6, True)], 5, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_533():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, []), (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_534():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, []), (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_535():
    assert api_bgp_nh_update_with_precondition([(0, [4, 4])], [v1:=(5, 0, False), (6, 0, False), v1], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_536():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False), (5, 0, False)], 3, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_537():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False), (5, 0, False)], 3, 3, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[3])])

def test_api_bgp_nh_update_with_precondition_538():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, True), (3, 5, False)], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_539():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False), (5, 0, True)], 3, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_540():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(8, [6, 6]), (7, [6]), (9, []), v1], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_541():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4, 3])], [(4, 0, False), (5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_542():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, [6, 6, 6]), v1], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_543():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(3, 0, False), (0, 0, False)], 4, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_544():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 5])], [(3, 0, False), (4, 0, False)], 5, 5, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_545():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (6, [9]), (6, [0, 0]), (7, [])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_546():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [7, 6, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_547():
    assert api_bgp_nh_update_with_precondition([v1:=(7, []), v1, v2:=(9, []), (8, [10]), v1, v2], [], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_548():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, [7, 6, 8, 9])], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_549():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6, 6, 6])], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_550():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, [6, 7, 6])], [], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_551():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(5, 0, False), v1, (7, 0, False), v1], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_552():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, v1, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_553():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [6, 6, 6])], [], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_554():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v3:=(0, []), v3], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_555():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3, 3])], [(4, 0, False), (5, 0, False)], 3, 3, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_556():
    assert api_bgp_nh_update_with_precondition([v1:=(7, []), v1, (8, [10]), v1, (8, []), (8, [0])], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_557():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1], [(0, 0, True), (0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_558():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, [6, 6, 6])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_559():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), v1], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_560():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_561():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [11]), v1, (7, []), v1, (9, []), (8, [0])], [], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_562():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_563():
    assert api_bgp_nh_update_with_precondition([v1:=(7, [5, 5]), v2:=(6, [5]), v2, v1], [(5, 8, False)], 5, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[5]), BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_564():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), (0, []), v1, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_565():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_566():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(4, 0, True), (5, 0, False), (6, 7, True)], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_567():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_568():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [4, 5, 4]), v1], [(4, 0, True), (5, 0, False)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_569():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_570():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v3:=(0, [7]), v3], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_571():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), (0, []), v1, (6, [8]), v1], [(7, 0, True)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_572():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(4, 0, False), (5, 0, True), (6, 0, True)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_573():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_574():
    assert api_bgp_nh_update_with_precondition([(0, [5])], [(4, 0, False), (6, 0, False), (7, 0, True)], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_575():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), v1, v1, v1, (9, [11]), v1, (10, [])], [], 11, 12, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[11])])

def test_api_bgp_nh_update_with_precondition_576():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), v2:=(0, []), v2, v2, (8, [7, 7]), v1], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_577():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [(4, 0, True), (5, 0, False), (6, 0, False)], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_578():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v1, (0, [8, 7])], [], 8, 8, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_579():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v3:=(0, []), v3, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_580():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v1, (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_581():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_582():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, v1, (0, [7, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_583():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), v1, (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_584():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_585():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (8, [6, 6, 6]), (7, []), (8, [])], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_586():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(4, 0, False), (5, 0, False), (6, 7, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_587():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_588():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_589():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [v1:=(4, 0, True), (5, 0, True), v1], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_590():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), v2, (0, [7])], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_591():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_592():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_593():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_594():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [(4, 0, False), (5, 0, False), (6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_595():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v2:=(0, [7]), v2], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_596():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_597():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v2:=(0, []), v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_598():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_599():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5, 5])], [(6, 0, False)], 5, 5, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_600():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v2:=(0, []), (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_601():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_602():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_603():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_604():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v2, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_605():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_606():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, []), v1, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_607():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v2, v1, (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_608():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [v1:=(5, 0, True), v2:=(6, 0, False), v2, v1], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_609():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), v1, (0, [7])], [], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_610():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_611():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, True), (5, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_612():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (7, [9]), (7, [])], [], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_613():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_614():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_615():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_616():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (8, [9]), v2:=(7, [9, 9]), v2], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_617():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1, (0, [8])], [], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_618():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_619():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_620():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), v1, (0, [7])], [], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_621():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [v1:=(4, 0, False), (6, 0, True), v1], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_622():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(4, 0, False), (5, 0, False), (6, 7, False)], 6, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_623():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_624():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, [7])], [(6, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_625():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_626():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_627():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (8, [7, 7]), (8, [0])], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_628():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [(4, 0, False), (5, 0, False), (6, 0, False)], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_629():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [(4, 0, False), (5, 0, False), (6, 0, False)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_630():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_631():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_632():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_633():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_634():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_635():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), v1, (0, [7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_636():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(4, 0, False), v1:=(5, 0, True), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_637():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_638():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_639():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, True), (5, 0, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_640():
    assert api_bgp_nh_update_with_precondition([v1:=(4, []), (4, [7]), v1], [(5, 0, False), (6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_641():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(8, [6, 6]), (7, [6, 6, 6]), v2], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_642():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(0, []), v2, v3, v1, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_643():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (8, [9]), (7, [])], [], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_644():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, [6, 5, 5])], [(5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_645():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, False), (5, 6, False)], 5, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_646():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v3:=(0, []), v1, v3, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_647():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [6])], [(4, 0, False), (5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_648():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, v1, v2], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_649():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [6])], [(4, 0, True), (5, 0, False)], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_650():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, True), (5, 6, False)], 5, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_651():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(5, 0, False), v2:=(7, 0, False), v1, v2], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_652():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, True), (6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_653():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(4, 0, False), v1:=(6, 0, True), v1], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_654():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [6])], [(4, 0, False), (5, 0, True)], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_655():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, []), (0, [7, 7])], [], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_656():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, []), (0, [8])], [], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_657():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [8]), (4, [])], [(6, 0, False), (7, 0, False)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_658():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, [7, 8])], [], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_659():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (8, [10]), (7, [])], [], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_660():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_661():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False), (5, 0, True)], 6, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_662():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), v1, v1, (0, []), (0, []), (9, [10]), v1], [], 10, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_663():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [v1:=(4, 0, False), (5, 0, False), v1], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_664():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), v1, v1], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_665():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (8, [9]), (7, [])], [], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=8, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_666():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False), (5, 6, True)], 5, 6, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_667():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, True), (6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_668():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (8, [9]), (7, [])], [], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=8, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_669():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, False), (5, 0, False)], 6, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_670():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [v1:=(5, 0, False), (6, 7, False), v1], 6, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=4, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_671():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (9, [7, 11]), (8, []), (10, [])], [], 11, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[11])])

def test_api_bgp_nh_update_with_precondition_672():
    assert api_bgp_nh_update_with_precondition([(0, []), (5, [7]), (4, [])], [(6, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_673():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2, (0, [7, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_674():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, []), (0, [7, 7])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_675():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [(6, 0, True)], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_676():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, False), (5, 0, False)], 6, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_677():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, True)], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_678():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, []), (0, [7, 7])], [], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_679():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_680():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_681():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, v1, (0, [8, 7, 8, 9])], [], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_682():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, (0, []), v2:=(0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_683():
    assert api_bgp_nh_update_with_precondition([v1:=(0, [5, 4]), v1], [v2:=(6, 0, False), v2, (7, 0, False)], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_684():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), (0, []), v2, v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_685():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), (0, []), v2, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_686():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), (0, []), v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_687():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v2, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_688():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, (0, []), (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_689():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, False), (5, 0, False)], 6, 6, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_690():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, v1, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_691():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_692():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [6])], [(6, 0, True)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_693():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, True)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_694():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, True)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_695():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_696():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [(6, 7, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_697():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_698():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [7])], [(6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_699():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [7])], [(6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_700():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [6])], [(6, 0, False)], 7, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_701():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (7, [9]), (6, [])], [(8, 0, False)], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=7, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_702():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [v1:=(5, 0, False), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_703():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6])], [(6, 7, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_704():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_705():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(4, 0, True), (5, 0, True), (6, 7, True)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_706():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [11]), (7, []), v1, v1, (9, []), (10, [11, 11])], [], 12, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_707():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, [7])], [(6, 0, False)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_708():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (9, [10, 7]), (8, [])], [], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_709():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [(6, 7, False)], 6, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_710():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, v1], [(0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_711():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [7, 7, 8])], [], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_712():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, False)], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_713():
    assert api_bgp_nh_update_with_precondition([v1:=(6, []), (0, []), (7, [5, 5, 5, 5]), v1], [(8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_714():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v1, (0, [])], [(0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_715():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, v2], [(0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_716():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [7])], [(6, 0, False)], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_717():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(4, 0, True), (5, 0, False), (6, 0, True)], 7, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_718():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (7, [9]), (6, [])], [(8, 0, False)], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_719():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [v1:=(5, 0, False), v1, (6, 0, True), (7, 8, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_720():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, []), v1], [(0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_721():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, v1], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_722():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(5, 0, False), (7, 0, False), v1, (8, 0, True)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_723():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(5, 0, False), v1:=(7, 0, False), (8, 0, True), v1], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_724():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(0, []), v1, v2, v2, v3, v3], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_725():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, (0, []), (0, []), v1, v1, v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_726():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v2:=(0, []), (0, []), v2, v1], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_727():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(4, 0, False), (5, 0, True), (6, 7, False)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_728():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(4, 0, False), (5, 0, False), (6, 0, True)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_729():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v2:=(0, []), v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_730():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(5, 0, True), (4, 6, True), (0, 0, False)], 4, 7, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_731():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(4, 0, False), (5, 0, False), (6, 7, True)], 6, 7, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_732():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_733():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), v1, (0, [8])], [(7, 0, True)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_734():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(0, []), v1, v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_735():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), (0, []), (8, [5, 10, 6, 7]), v1], [(9, 0, False)], 10, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_736():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, [6, 6])], [(7, 0, False)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_737():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), (0, []), v1, (0, []), v2], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_738():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v3:=(0, []), (0, []), v3], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_739():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(0, []), v2, v1, (0, []), v3], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_740():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), (0, []), v2, v1, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_741():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v2, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_742():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), (0, []), v2, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_743():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(5, 0, False), (7, 0, False), v1:=(8, 0, True), v1], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_744():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6, 6])], [(6, 7, False)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_745():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), v2, v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_746():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v3:=(0, []), (0, []), v3], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_747():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, (0, []), (0, []), (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_748():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [v1:=(5, 0, False), (6, 0, False), v1, (7, 0, False)], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_749():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v2, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_750():
    assert api_bgp_nh_update_with_precondition([(4, [6]), (3, [])], [(5, 0, False), (6, 7, False), (0, 0, True)], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=4, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_751():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [v1:=(5, 0, False), (7, 0, True), (8, 0, False), v1], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_752():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), v1, (9, [11]), v1, (9, [0]), v2:=(10, []), v2], [], 11, 12, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[11])])

def test_api_bgp_nh_update_with_precondition_753():
    assert api_bgp_nh_update_with_precondition([(3, [4]), (3, [0])], [(4, 5, True), (0, 0, False), (0, 0, False)], 4, 5, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_754():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (0, []), v2:=(0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_755():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), (0, []), v1, (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_756():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(4, 0, False), (5, 0, False), (6, 7, True)], 6, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_757():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [4])], [(5, 0, False), (4, 0, False), (0, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_758():
    assert api_bgp_nh_update_with_precondition([(5, [9]), (4, [])], [(6, 0, True), (7, 0, False), (8, 0, False)], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=5, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_759():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_760():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_761():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, (0, []), (0, []), v1, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_762():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_763():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_764():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_765():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [v1:=(4, 0, True), (5, 0, True), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_766():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_767():
    assert api_bgp_nh_update_with_precondition([(0, [7])], [v1:=(5, 0, False), (6, 0, False), v1, (7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_768():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6, 6])], [(7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_769():
    assert api_bgp_nh_update_with_precondition([(5, [9]), (4, [])], [(6, 0, False), (7, 0, False), (8, 0, True)], 9, 9, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_770():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [(5, 0, False), v1:=(6, 0, False), (7, 0, False), v1], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_771():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1, (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_772():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [3])], [(3, 4, False), (0, 0, False), (0, 0, False)], 3, 5, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_773():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_774():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(4, 0, False), (5, 0, False), (6, 0, False)], 7, 7, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_775():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5])], [(4, 0, False), (6, 0, False), (7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_776():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, (0, []), (0, [9])], [], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_777():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(4, 0, False), (5, 0, False), (6, 0, False)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_778():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), v1:=(0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_779():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_780():
    assert api_bgp_nh_update_with_precondition([v1:=(9, []), v1, v2:=(11, []), (0, []), (10, [8, 8]), v1, v2], [], 12, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_781():
    assert api_bgp_nh_update_with_precondition([(5, [7]), (4, [])], [(6, 0, False), (8, 0, False), (9, 0, True)], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_782():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), (0, []), (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_783():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (6, [7]), (6, [0, 0])], [(7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_784():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (8, [11]), (7, []), (9, []), (10, [12, 11])], [], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_785():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, False), v1:=(5, 0, False), v1], 6, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_786():
    assert api_bgp_nh_update_with_precondition([(5, [9]), (4, [])], [(6, 0, False), (7, 0, False), (8, 0, False)], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=5, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_787():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [(5, 6, False), (0, 0, True)], 5, 6, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_788():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v3:=(0, []), v3], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_789():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_790():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, [5])], [(4, 0, False), v2:=(6, 0, False), v2], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_791():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), (0, []), v1, v2], [(0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_792():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1], [(0, 0, False), (0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_793():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v1, v2, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_794():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(0, []), (0, []), v2], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_795():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, v3:=(0, []), v3], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_796():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (0, [7, 7])], [(7, 0, True)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_797():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2, v1, v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_798():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, False), (7, 0, True)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_799():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v1, v1, v1], [(0, 0, True), (0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_800():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [7])], [(5, 0, False), (6, 0, False)], 7, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_801():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [7])], [(5, 0, False), (6, 0, True)], 7, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_802():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [6])], [(5, 0, False), (6, 7, False)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_803():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, (0, []), v1, v1, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_804():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), v1, (0, []), (0, [])], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_805():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), (0, []), v1, (0, [])], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_806():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, v2:=(0, []), (0, []), v2, (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_807():
    assert api_bgp_nh_update_with_precondition([v1:=(9, [13]), (8, []), (10, []), v1, v1, (11, []), (12, [13])], [], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_808():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [7, 6, 6, 6])], [(8, 0, False)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_809():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), v1, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_810():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), (0, [])], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_811():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [8])], [(7, 0, False)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_812():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [7])], [(7, 0, False)], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_813():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (9, [7, 10, 7, 7]), (8, [7])], [], 10, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_814():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v2, (0, [7, 9, 7])], [(8, 0, True)], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_815():
    assert api_bgp_nh_update_with_precondition([v1:=(10, [12]), v1, v2:=(9, [12]), v1, v2, v3:=(11, []), v1, v3], [], 13, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_816():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v2:=(0, []), v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_817():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), (0, []), v2], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_818():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2, (0, [8])], [(7, 0, False)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_819():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), (0, []), v1, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_820():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (8, [10]), (8, []), (9, [10])], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_821():
    assert api_bgp_nh_update_with_precondition([v1:=(9, []), v2:=(10, [14]), v1, v2, v1, (11, []), v1, (12, [])], [], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_822():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, []), (0, [8])], [(7, 0, True)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_823():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(5, 0, False), (7, 0, False), (6, 8, False), (0, 0, True)], 6, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_824():
    assert api_bgp_nh_update_with_precondition([(0, [9])], [(5, 0, False), (6, 0, False), (7, 0, True), (8, 0, True)], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_825():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, [8])], [(7, 0, False)], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_826():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), (0, [7])], [(7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_827():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [v1:=(5, 0, True), (6, 0, True), (7, 0, False), v1], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_828():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5, 5])], [(6, 0, True), (5, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_829():
    assert api_bgp_nh_update_with_precondition([(0, [9])], [(5, 0, True), (6, 0, True), (7, 0, False), (8, 0, False)], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_830():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [(5, 0, False), (6, 0, False), (7, 0, False), (8, 9, True)], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_831():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [(5, 0, False), (6, 0, False), (7, 0, False), (8, 9, False)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_832():
    assert api_bgp_nh_update_with_precondition([(0, [9])], [(5, 0, False), (6, 0, False), (7, 0, False), (8, 0, False)], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_833():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [(5, 0, True), (6, 0, False), (7, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_834():
    assert api_bgp_nh_update_with_precondition([(0, []), (9, [13]), (8, []), v1:=(10, []), v1, (11, []), (12, [])], [], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_835():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v3:=(0, []), v4:=(0, []), v3, v4, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_836():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, False), v1:=(7, 0, True), v1], 8, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_837():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [9]), v1, v2:=(7, []), (8, [0]), v2, (8, [0])], [(9, 10, True)], 9, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=8, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_838():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(5, 0, False), v1:=(7, 0, True), v1, (8, 0, False)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_839():
    assert api_bgp_nh_update_with_precondition([v1:=(12, []), v2:=(9, [11]), v2, (8, []), v2, (10, [11, 11]), v1], [], 11, 11, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_840():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, []), (9, [10]), (8, [10])], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_841():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v2, (0, [])], [v3:=(0, 0, False), v3], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_842():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [v1:=(5, 0, False), (7, 0, False), (8, 0, True), v1], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_843():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, False), v1:=(7, 0, True), v1], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_844():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v3:=(0, []), v3, v1, v2, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_845():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False), (5, 6, True), (0, 0, True)], 5, 7, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[5])])

def test_api_bgp_nh_update_with_precondition_846():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v1, (0, []), v1, (0, [])], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_847():
    assert api_bgp_nh_update_with_precondition([v1:=(8, []), v2:=(8, [10]), v1, v2, v1, (8, [0, 0, 0]), (9, [10])], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_848():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), (0, []), v1, v2], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_849():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v2, (0, []), v1, (0, [8, 9, 8])], [], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_850():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v3:=(0, []), v3, (0, []), v2, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_851():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, [7, 8])], [(8, 0, True)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_852():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v2:=(0, []), v2], [(0, 0, True), (0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_853():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [6, 6])], [v1:=(7, 0, False), v1], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_854():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(5, 0, False), (7, 0, False), (8, 0, False), (9, 0, False)], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_855():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), v1:=(6, 0, True), (7, 0, False), v1], 8, 8, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_856():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v1, (0, [7, 7])], [(8, 0, False)], 9, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_857():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, True), v1:=(7, 0, False), v1], 8, 8, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_858():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, (0, []), v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_859():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(5, 0, False), (7, 0, True), v1:=(8, 0, False), v1], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_860():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), (0, []), (0, []), v1, v2, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_861():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v2, (0, []), (0, []), (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_862():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, True), (5, 0, True), (6, 0, False)], 7, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_863():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), v1, v2:=(0, []), v2, v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_864():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, (0, []), v2, v1, (0, []), v1], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_865():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [v1:=(5, 0, False), (6, 0, False), (7, 0, False), v1], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_866():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), v2:=(0, []), v1, (0, []), v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_867():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (8, [10]), (7, []), (8, [])], [(9, 0, False)], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_868():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [11]), v2:=(7, []), (9, []), (8, [0]), v2, v1], [(10, 0, False)], 12, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_869():
    assert api_bgp_nh_update_with_precondition([v1:=(8, [11]), (7, [13]), (9, []), (10, [11, 11, 11]), v1, (12, [])], [], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_870():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [5, 5])], [(6, 0, True), v1:=(7, 0, True), (8, 0, True), v1], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_871():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [5])], [(4, 0, False), (6, 0, False), (7, 0, False)], 8, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_872():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(10, [8, 8]), v2, v3:=(9, [8, 8]), v3], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_873():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(5, 0, False), v1:=(7, 0, False), (8, 0, False), v1], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_874():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), (0, []), v2:=(0, []), v2, (0, [9, 9])], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_875():
    assert api_bgp_nh_update_with_precondition([v1:=(10, [12]), v2:=(9, []), v1, v2, v1, v3:=(10, []), v3, (10, [])], [], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_876():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), v1, (0, []), (0, [9, 9])], [], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_877():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [6])], [(4, 0, False), (5, 0, True), (6, 7, False)], 6, 8, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_878():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), v1:=(6, 0, False), (7, 0, False), v1], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_879():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, [])], [(0, 0, True), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_880():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [v1:=(5, 0, False), (6, 0, False), (7, 0, False), v1], 8, 9, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_881():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [v1:=(5, 0, False), (6, 0, False), (7, 0, False), v1], 8, 8, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_882():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v2], [(0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_883():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6])], [(6, 7, False), (0, 0, True)], 6, 8, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6])])

def test_api_bgp_nh_update_with_precondition_884():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v2, v1], [(0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_885():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, []), (0, []), (0, []), (0, [])], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_886():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, (9, [7, 7]), (8, [])], [(10, 0, False)], 7, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_887():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v1, v2, (0, []), v1, (0, [10, 10])], [], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_888():
    assert api_bgp_nh_update_with_precondition([(6, [10]), (5, [])], [v1:=(7, 0, False), (8, 0, False), v1, (9, 0, True)], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=6, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_889():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), (0, [7])], [(6, 0, False), (7, 8, False)], 7, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_890():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, False), (8, 0, True)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_891():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, v2, v3:=(0, []), (0, []), v3, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_892():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), v1, (0, [8])], [(6, 0, False), (7, 0, False)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_893():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v3:=(0, []), v4:=(0, []), v1, v3, v2, v4], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_894():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), v1, v2:=(0, []), v2], [(0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_895():
    assert api_bgp_nh_update_with_precondition([v1:=(7, []), (0, []), (8, [11, 6, 11]), v1, (9, [10, 10])], [(11, 0, True)], 12, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_896():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), v1, (0, []), (0, []), (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_897():
    assert api_bgp_nh_update_with_precondition([v1:=(11, [15]), (10, []), (12, []), v1, v1, v1, (11, []), v1, (13, [])], [], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_898():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, [5, 5, 7, 5])], [(6, 0, False), (7, 0, False)], 8, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_899():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, True), (7, 0, False), (8, 9, True)], 8, 9, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_900():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, True), (6, 0, True), (7, 0, False), (8, 9, False)], 8, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_901():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [9])], [(5, 0, True), (6, 0, True), (7, 0, True), (8, 0, True)], 9, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_902():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, [7])], [(6, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_903():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), (0, []), (0, []), v1, (12, [15]), v1, v1, v1, (13, []), v1], [], 14, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_904():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, v1, (9, [11]), (8, [])], [(10, 0, False)], 11, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=9, nexthops=[11])])

def test_api_bgp_nh_update_with_precondition_905():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), (0, []), (0, []), (0, []), v1, (0, [])], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_906():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(6, []), (7, [9]), v1], [(8, 0, False), (10, 0, False)], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_907():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [9])], [(5, 0, False), (6, 0, False), (7, 0, True), (8, 0, False)], 9, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_908():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v1, v1, v2], [(0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_909():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [9])], [(5, 0, True), (6, 0, True), (7, 0, False), (8, 0, False)], 9, 9, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_910():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), v1, (0, [])], [(0, 0, False), (0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_911():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), v1, v1, (0, [])], [(0, 0, True), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_912():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v1, v2:=(12, []), v1, (11, [13]), (10, []), v2], [], 13, 13, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_913():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, v2, v1, (0, [10])], [(9, 0, True)], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_914():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (6, [9]), (6, []), (7, [])], [(8, 0, False), (10, 0, False)], 11, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_915():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, True), (6, 0, False), (7, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_916():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [6, 6])], [(7, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_917():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [9])], [(5, 0, False), (6, 0, False), (7, 0, True), (8, 0, False)], 9, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[9])])

def test_api_bgp_nh_update_with_precondition_918():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, True), (7, 0, False), (8, 9, False)], 8, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_919():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v2, v3:=(0, []), (0, []), v4:=(0, []), v4, v3], [], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_920():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [(5, 0, True), (7, 0, False), (8, 0, False), (9, 0, False)], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_921():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, (0, []), v1], [(0, 0, False), (0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_922():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), v1, (0, []), v1, (0, []), v1, (11, [14]), (10, [12, 12]), v1], [], 14, 15, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_923():
    assert api_bgp_nh_update_with_precondition([v1:=(10, []), v2:=(0, []), v2, (0, []), v1, v1, (11, [13]), v1, (12, [13])], [], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[13]), BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_924():
    assert api_bgp_nh_update_with_precondition([(0, [10])], [v1:=(6, 0, False), (7, 0, False), (8, 0, True), v1, (9, 0, False)], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_925():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [v1:=(6, 0, True), (8, 0, False), v2:=(9, 0, False), v1, v2], 10, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_926():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [8, 6, 7])], [(8, 0, True), (9, 0, False)], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_927():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [v1:=(6, 0, True), (8, 0, False), v2:=(9, 0, False), v2, v1], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_928():
    assert api_bgp_nh_update_with_precondition([(8, [12]), v1:=(7, []), (9, []), (10, []), v1, (11, [12, 12])], [(12, 0, False)], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_929():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(5, 0, False), (6, 0, False), (7, 0, False), (8, 9, False)], 8, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_930():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, [5])], [(5, 0, False), (0, 0, True), (0, 0, False)], 6, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_931():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v2:=(0, []), (0, []), v2, v1, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_932():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v1, (0, []), (0, [7, 9, 7])], [(9, 0, False), (8, 0, False)], 10, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_933():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, (0, []), v2:=(0, []), v2], [(0, 0, False), (0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_934():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7, 8])], [(5, 0, False), (6, 0, True), (7, 0, False), (8, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_935():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), v1:=(0, []), (0, []), v1], [(0, 0, True), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_936():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(0, []), v1, v4:=(0, []), v4, v2, v3, v2, v4, v2], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_937():
    assert api_bgp_nh_update_with_precondition([(0, []), (7, [11]), (6, []), (8, [10]), (9, [])], [(12, 0, False), (13, 0, False)], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_938():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), (0, []), (0, []), v1], [(0, 0, False), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_939():
    assert api_bgp_nh_update_with_precondition([v1:=(9, []), v2:=(11, []), (10, [8, 8]), v1, v2, (12, [8, 8, 8, 8, 13, 14, 8])], [], 15, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_940():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v2:=(10, [13]), (9, [13]), (10, [0]), v2, (10, []), v1, (12, [])], [], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_941():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, (0, []), v1, (0, []), (0, []), v2], [(0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_942():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(11, []), v2:=(0, []), v2, v2, v3:=(12, [10, 10, 10]), v1, v3, v1], [], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_943():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(12, []), (0, []), v1, v1, (11, [14]), (10, []), v2, (11, [])], [], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_944():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(10, [12]), v2, (10, []), v3:=(11, [12]), (10, []), v2, v3], [], 12, 12, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[12]), BgpdRouteEvent(op=BOp.SET, prefix=10, nexthops=[12])])

def test_api_bgp_nh_update_with_precondition_945():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v1, v2:=(0, []), v1, (0, []), (0, []), v2, (0, [])], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_946():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (11, [9, 8]), (10, [9])], [(12, 0, False)], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_947():
    assert api_bgp_nh_update_with_precondition([(0, [6])], [(7, 0, False), (8, 0, False), (6, 9, False), (0, 0, False), (0, 0, True)], 6, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_948():
    assert api_bgp_nh_update_with_precondition([v1:=(11, [14]), v2:=(10, []), v2, v2, v1, v1, (12, []), (13, [14, 14]), (15, [])], [], 14, 16, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=13, nexthops=[14]), BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_949():
    assert api_bgp_nh_update_with_precondition([v1:=(10, []), v2:=(12, []), (11, [17]), v1, v2, (13, []), v1, (14, []), (15, [])], [], 16, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_950():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(0, []), v1, v1, v3, v2, (12, [10, 10]), (11, [])], [], 10, 13, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=12, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_951():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, (0, []), (0, []), v2], [(0, 0, False), (0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_952():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), v2:=(0, []), v1, (0, []), v2], [(0, 0, False), (0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_953():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [v1:=(7, 0, True), (8, 0, False), (6, 0, False), v1, (0, 0, False)], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_954():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), (0, []), (0, []), v1, (0, [8, 8, 9])], [(10, 0, False)], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_955():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [v1:=(6, 0, True), (8, 0, False), (9, 0, False), (10, 0, False), v1], 11, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_956():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v2, v1], [(0, 0, False), (0, 0, False), (0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_957():
    assert api_bgp_nh_update_with_precondition([v1:=(13, [18]), v1, v2:=(12, []), v2, v1, v1, v1, v1, (14, []), (15, []), (16, [])], [], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_958():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [v1:=(6, 0, False), (7, 0, True), (8, 0, False), (9, 0, False), v1], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_959():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(11, []), v1, v1, v3:=(0, []), v3, (0, []), (12, [10, 13, 10]), v2], [], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_960():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), (0, []), v2, v1, v1, (11, [13]), (10, []), (12, [13, 13])], [], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[13]), BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_961():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [v1:=(6, 0, False), (8, 0, False), (9, 0, False), v1, (10, 0, False)], 11, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_962():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [v1:=(6, 0, True), (7, 0, False), (8, 0, False), (9, 0, False), v1], 10, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_963():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), (0, []), v1], [v2:=(0, 0, True), (0, 0, False), v2], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_964():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(6, 0, False), v1:=(7, 0, False), (8, 0, False), (9, 0, True), v1], 10, 10, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_965():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, v2:=(0, []), v2, (0, [])], [(0, 0, False), v3:=(0, 0, True), v3], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_966():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v1, (0, []), (0, [8, 8])], [v2:=(8, 0, False), v2], 9, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_967():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(6, 0, False), (8, 0, False), v1:=(9, 0, False), (10, 0, False), v1], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_968():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(12, []), v1, v3:=(11, [15]), (10, []), v3, v2, (13, []), (14, [15])], [], 16, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_969():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(6, 0, False), (7, 0, False), v1:=(8, 0, False), v1, (9, 0, False)], 10, 11, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_970():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), (0, []), v2, (0, []), v1], [(0, 0, True), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_971():
    assert api_bgp_nh_update_with_precondition([(0, [8])], [v1:=(9, 0, True), v2:=(10, 0, True), v1, v1, (8, 11, False), v2, (0, 0, False)], 8, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[8])])

def test_api_bgp_nh_update_with_precondition_972():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [v1:=(6, 0, False), (7, 0, False), (8, 0, False), (9, 0, False), v1], 10, 11, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_973():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(10, []), v2, v2, (0, []), v3:=(11, [13]), v3, v2], [(12, 0, False)], 13, 14, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=11, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_974():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), (0, []), v1, (0, [])], [(0, 0, True), (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_975():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v3:=(0, []), v3, v4:=(0, []), v2, v2, v2, (0, []), v1, v4], [], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_976():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v2:=(0, []), v2, v1, v1, (12, [10, 10]), v1, (13, [10, 10, 10]), (14, [])], [], 15, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_977():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), v3:=(11, [13]), (10, []), v3, (12, [13, 13])], [], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[13]), BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_978():
    assert api_bgp_nh_update_with_precondition([v1:=(12, []), v1, (8, [10]), (7, [10, 9, 10]), (11, []), v1], [(10, 0, True), (13, 0, False)], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_979():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, [6, 7, 6])], [(7, 8, False), (6, 0, True), (0, 0, False)], 7, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[6, 7])])

def test_api_bgp_nh_update_with_precondition_980():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(12, []), v2, v1, (11, [14]), (10, []), v3, (13, [14, 14])], [], 14, 15, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=13, nexthops=[14]), BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_981():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [8])], [(6, 0, False), (7, 0, False), (9, 0, True), (8, 10, True), (0, 0, True)], 8, 10, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_982():
    assert api_bgp_nh_update_with_precondition([v1:=(9, [13]), v1, v2:=(8, [13]), (10, []), v2, (11, [12, 12]), (9, [0, 0])], [(13, 0, False)], 14, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_983():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v1, v1, v2, (0, []), v2], [(0, 0, False), (0, 0, True), (0, 0, True)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_984():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, []), (0, []), (0, []), v1:=(0, []), v1, (12, [10, 10, 10]), (11, [])], [], 13, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_985():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), (0, []), (0, []), v2:=(0, []), (0, []), v2, (0, []), v1], [(0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_986():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [11])], [(6, 0, True), (7, 0, True), (8, 0, True), (9, 0, False), (10, 0, True)], 11, 11, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_987():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), v1, (0, []), (0, [9])], [(9, 10, False), (0, 0, False)], 9, 11, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_988():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, (0, []), (0, []), v1, (11, [10, 13]), (11, [])], [(12, 0, False)], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_989():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v1, v1, v1, (0, []), (10, [11]), (9, [])], [(11, 0, False), (0, 0, True)], 12, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_990():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [7])], [(6, 0, False), (8, 0, True), (9, 0, False), (10, 0, False), (11, 0, False)], 12, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_991():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, (0, []), v1, (11, [14]), (10, []), (12, [])], [(13, 0, False)], 15, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_992():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, (0, []), (0, []), v2:=(0, []), v2], [(0, 0, False), (0, 0, False), (0, 0, False)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_993():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v2:=(0, []), v1, v2, v1, (12, [11, 11]), (12, []), (13, []), (14, [])], [], 11, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[11])])

def test_api_bgp_nh_update_with_precondition_994():
    assert api_bgp_nh_update_with_precondition([v1:=(14, [12, 12]), v2:=(13, []), v2, v1, v3:=(15, []), v2, v1, v2, v3, v3, (16, [12, 17])], [], 17, 18, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=16, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_995():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), (0, [7])], [(6, 0, False), (8, 0, True), v1:=(9, 0, True), (10, 0, False), v1], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_996():
    assert api_bgp_nh_update_with_precondition([(0, [12])], [v1:=(8, 0, True), v2:=(9, 0, False), v3:=(10, 0, True), v1, v2, v3, (11, 0, False)], 12, 13, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[12])])

def test_api_bgp_nh_update_with_precondition_997():
    assert api_bgp_nh_update_with_precondition([(10, [11]), v1:=(9, [11, 11]), v2:=(12, []), (13, [11, 11, 11, 11, 14, 15, 11, 16]), v1, v2], [], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_998():
    assert api_bgp_nh_update_with_precondition([v1:=(15, []), v2:=(13, []), (12, [9, 9, 9, 10, 9]), (11, []), v2, (14, [9, 9]), v1, (16, [])], [], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_999():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v2:=(13, []), (0, []), v2, v1, (12, [10, 10]), v1, v2, (14, [])], [(15, 0, False)], 10, 16, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=12, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1000():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(6, 0, False), (7, 0, True), (8, 0, False), (9, 0, False), (10, 11, False)], 10, 12, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1001():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), v2:=(0, []), (0, []), v2, (11, [14]), (10, []), (12, []), v1, v1], [(14, 15, True)], 14, 15, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=11, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1002():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), (0, []), v2, v3:=(0, []), v3], [v4:=(0, 0, False), v4, (0, 0, False)], 0, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1003():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), (0, []), (0, []), v1, v1, v1, (12, [14]), v1, (12, []), (13, [])], [(14, 15, False)], 14, 15, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_1004():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(15, []), v2, v1, (0, []), (0, []), (0, []), (13, [17]), (12, []), (14, []), v2], [], 16, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1005():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v2:=(11, [16]), v2, v1, v3:=(12, []), v1, (13, []), (14, []), v2, v3], [(15, 0, False)], 16, 17, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[16])])

def test_api_bgp_nh_update_with_precondition_1006():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(14, []), v1, v2, v3:=(12, []), v4:=(13, [17]), v4, v3, (13, [0]), v2, (15, [])], [], 16, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1007():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), v2:=(15, []), v2, v3:=(14, [19]), v1, v1, v1, v2, (14, []), v3, (16, []), (17, [])], [], 18, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1008():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(14, []), (0, []), v1, (12, [16]), (11, []), (13, []), (12, [0]), v2, (15, [16])], [], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1009():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(10, []), v3:=(0, []), (0, []), v1, v3, (11, [13]), v2, v2], [v4:=(12, 0, False), v4], 13, 14, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=11, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_1010():
    assert api_bgp_nh_update_with_precondition([(0, []), v1:=(0, []), v1, (0, []), (0, []), (0, [10, 9])], [(7, 0, False), (9, 0, True), (8, 0, False)], 10, 11, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10, 9])])

def test_api_bgp_nh_update_with_precondition_1011():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), (0, [7, 10])], [(10, 0, True), (8, 0, False), (9, 0, False)], 11, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1012():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v2, (0, []), v1, (11, [13]), (10, []), (12, [13, 13])], [(13, 14, True)], 13, 14, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=12, nexthops=[]), BgpdRouteEvent(op=BOp.DEL, prefix=11, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1013():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), (0, []), v1, (0, [7])], [(6, 0, True), (7, 8, False), (0, 0, False), (0, 0, False)], 7, 9, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[7])])

def test_api_bgp_nh_update_with_precondition_1014():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v2:=(12, []), (0, []), (12, [15]), v1, v3:=(13, [15, 14]), v3, v2, (16, []), (12, [])], [], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1015():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), (0, []), v2:=(11, [16]), (11, []), v2, (12, [16]), v1, (14, []), v2, (15, [16, 16, 16])], [], 17, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1016():
    assert api_bgp_nh_update_with_precondition([v1:=(16, []), v2:=(14, [19]), (13, []), v3:=(15, []), v3, v1, v2, v1, v4:=(17, []), v4, (14, []), v3], [], 18, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1017():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), (0, []), v2:=(0, []), v2, v1, v3:=(13, [14]), (11, []), (12, []), v1, v3], [(14, 15, False)], 14, 16, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=13, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_1018():
    assert api_bgp_nh_update_with_precondition([v1:=(12, []), (0, []), v2:=(0, []), v2, v3:=(13, [15]), v1, v1, (14, [15, 15]), v3, v3, (16, [15, 17])], [], 18, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1019():
    assert api_bgp_nh_update_with_precondition([v1:=(12, [18]), v2:=(11, []), v3:=(13, [17]), v1, (14, []), (15, []), v3, (13, []), (16, [18, 18]), v2], [], 19, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1020():
    assert api_bgp_nh_update_with_precondition([v1:=(11, []), v1, v2:=(0, []), v3:=(13, []), v2, (12, [16]), v1, v3, (14, []), (12, [0])], [(15, 0, False)], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1021():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), (0, []), v2:=(0, []), v1, v1, v3:=(14, []), v2, v1, (0, []), (0, []), (15, [13, 13]), v3], [], 13, 16, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=15, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1022():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(7, 0, False), (8, 0, False), v1:=(9, 0, False), (11, 0, False), (10, 12, False), v1], 10, 13, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_1023():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), v1, v2:=(14, [19]), v1, v3:=(14, []), v4:=(15, []), v1, v3, (16, [18]), (17, []), v2, v4], [], 20, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1024():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(7, 0, False), (8, 0, False), (9, 0, False), (11, 0, False), v1:=(10, 12, False), v1], 10, 12, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[10])])

def test_api_bgp_nh_update_with_precondition_1025():
    assert api_bgp_nh_update_with_precondition([v1:=(15, []), v2:=(14, []), v1, (13, [12, 12]), (13, []), v2, v1, v2, (16, []), (13, []), (13, [0, 0])], [], 12, 17, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=13, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1026():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(13, []), v2, v1, v3:=(0, []), v1, (0, []), (0, []), v3, (14, [16]), v2], [(15, 0, False)], 17, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1027():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(11, []), v2, v1, v1, v4:=(11, [14]), v3, v4, (12, [13, 13])], [(14, 15, False)], 14, 16, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=11, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1028():
    assert api_bgp_nh_update_with_precondition([v1:=(12, []), v2:=(13, []), (12, [16]), v3:=(12, []), v3, v1, v2, v1, (14, []), v2, (15, [])], [(16, 17, False)], 16, 18, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=12, nexthops=[16])])

def test_api_bgp_nh_update_with_precondition_1029():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [13])], [(8, 0, True), (9, 0, True), v1:=(10, 0, False), v2:=(11, 0, False), v1, (12, 0, False), v2], 13, 13, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_1030():
    assert api_bgp_nh_update_with_precondition([v1:=(14, []), v2:=(12, []), (0, []), v2, v1, v1, (13, [17]), v2, v1, (15, []), (16, [17, 17])], [(17, 18, False)], 17, 19, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=16, nexthops=[17]), BgpdRouteEvent(op=BOp.SET, prefix=13, nexthops=[17])])

def test_api_bgp_nh_update_with_precondition_1031():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [10])], [(7, 0, False), (8, 0, False), (9, 0, True), (11, 0, False), (10, 12, True), (0, 0, False)], 10, 12, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1032():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v2, v1, (0, []), v1, (0, [])], [(0, 0, False), (0, 0, False), (0, 0, False), (0, 0, True)], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1033():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [12])], [(8, 0, False), v1:=(9, 0, False), v2:=(10, 0, False), v2, (11, 0, True), v1, (12, 0, False)], 13, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1034():
    assert api_bgp_nh_update_with_precondition([v1:=(12, []), (13, [17]), v1, (14, []), v2:=(13, []), v1, v1, (13, []), (15, []), (13, [0]), v2], [(16, 0, False)], 18, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1035():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [6])], [v1:=(9, 0, False), (10, 0, False), v2:=(6, 11, True), v2, (0, 0, True), (0, 0, False), v1, v2], 6, 11, False) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.DEL, prefix=0, nexthops=[])])

def test_api_bgp_nh_update_with_precondition_1036():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [13])], [v1:=(8, 0, False), v2:=(9, 0, False), (10, 0, False), (11, 0, False), v1, v2, (12, 0, False)], 13, 13, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=0, nexthops=[13])])

def test_api_bgp_nh_update_with_precondition_1037():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v2, v2, v3:=(12, [11, 11]), (12, [0]), (13, [14, 14]), (15, []), v3], [(14, 16, False)], 14, 17, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=13, nexthops=[14])])

def test_api_bgp_nh_update_with_precondition_1038():
    assert api_bgp_nh_update_with_precondition([v1:=(14, [19]), v2:=(14, [0]), v3:=(15, []), v4:=(16, []), v2, v2, v1, v3, v3, (17, []), v1, v4, v4], [(18, 0, False)], 20, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1039():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(0, []), v1, (0, []), (0, []), v2, (0, []), v3:=(13, [16]), (13, [0, 0, 0, 0]), (14, []), v3], [], 15, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1040():
    assert api_bgp_nh_update_with_precondition([v1:=(16, []), v2:=(13, []), (0, []), v1, v3:=(0, []), v3, v3, v4:=(14, [17]), v2, (15, [17]), v1, v4], [(18, 0, True)], 19, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1041():
    assert api_bgp_nh_update_with_precondition([v1:=(17, []), (0, []), v2:=(16, []), v1, (14, [12, 12]), v3:=(13, []), v4:=(15, []), v2, v1, v3, v4], [(12, 18, False)], 12, 19, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=14, nexthops=[12])])

def test_api_bgp_nh_update_with_precondition_1042():
    assert api_bgp_nh_update_with_precondition([(12, [21]), v1:=(11, []), v2:=(13, [21]), (14, []), (15, [21]), (16, [17, 17]), v2, (18, [19, 19, 19]), v1, (20, [17])], [], 22, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1043():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v2:=(0, []), v3:=(17, []), v2, v3, v1, v4:=(13, [16]), v4, (13, [0, 0]), (14, []), (15, [16, 16, 16]), v3], [], 18, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1044():
    assert api_bgp_nh_update_with_precondition([v1:=(13, []), v1, (0, []), v1, v2:=(14, [17]), v1, (14, []), v2, (15, []), (16, [17, 18]), (14, [0, 0]), (14, [0, 0])], [], 18, 19, True) == DownstreamMsgs(msgs=[BgpdRouteEvent(op=BOp.SET, prefix=16, nexthops=[18])])

def test_api_bgp_nh_update_with_precondition_1045():
    assert api_bgp_nh_update_with_precondition([v1:=(14, []), v2:=(0, []), (0, []), v2, v3:=(0, []), v4:=(16, []), v2, v3, (0, []), (15, [13, 13]), v1, v4], [(17, 0, False)], 18, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1046():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, []), v1:=(0, []), (0, []), (0, []), (0, []), v1], [(0, 0, False), (0, 0, False), v2:=(0, 0, True), (0, 0, False), v2], 0, 0, True) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1047():
    assert api_bgp_nh_update_with_precondition([v1:=(0, []), v1, v2:=(16, []), v1, v2, (15, [14, 13]), v3:=(15, []), v2, v3, (17, []), (18, []), (19, [20, 14])], [(21, 0, True)], 22, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1048():
    assert api_bgp_nh_update_with_precondition([(0, []), (0, [13])], [v1:=(9, 0, False), v2:=(10, 0, False), (11, 0, False), (12, 0, False), (14, 0, False), v1, (13, 0, False), v2], 15, 0, False) == DownstreamMsgs(msgs=[])

def test_api_bgp_nh_update_with_precondition_1049():
    assert api_bgp_nh_update_with_precondition([v1:=(17, []), v2:=(0, []), v3:=(14, []), v2, (15, [20]), v3, (16, [20]), v1, v3, (18, [21]), v1, (19, [20, 20, 20]), (15, [0, 0])], [], 22, 0, True) == DownstreamMsgs(msgs=[])

