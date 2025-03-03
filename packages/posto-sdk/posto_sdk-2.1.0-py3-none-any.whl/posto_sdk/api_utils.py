
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c$}40-*3|}5Pr{JaS9JjQJV-JD-CIE0|sNOwjv%7ioE2~nk9Cy9ZFaAf9ISyX%pB~@{nGx-~IaT&d!u9z-&q`mcWZrDg);{F%viy8_y{e{;W_N-G1kCxg@;jSpgNCw3={<=Bm~O{#<G!@6JE@W6w)+rZt?-FVAw0!puCN$M^lWOruppQtM&O%?c7(6jDG|iNtUzSkBFcu(eJ7N-={t=7O6z4m9T31n$XET&a8p+NcSz%B*4|A5heaaTCx5y(B|UULO(6>M(o<>V#9Z)O%a|>;u)gf4RK^nbm&2N|nwPQk`6A!$g8T!^4zLNv3!_VYWc1wTBsYvMnxbLlVuc7%HlYm%%6+jr-sgvJ{mj?6w!)w=t#Sk9A0Y2AL(FC$QZow(}=_n=>g4<vCq!N+c7Xm1XXdj(%uz)4_Lx?$8{>DAH1LVO)z!W>!r%VEV@X_L}mx;&}>;x}N9IT3ULKX-ebTHnOv{DhM!KhTuo*a%$6!GCeJ6Dp5thUPZ}@34yux$30)&$1R#li9w`yPo{U+HdUJv#oJy3cUzm)ZaB#Wd%)POnB%HIYF6roxeez&U%q@;GoqlT(XQ&ZT21Tvy~pThatln<v^ek0exXuQ0ac&oc8QPRw@v56Vlj6g5WK%wOkjR<M{hJq*k^H{^Iu)*;o4#dm!`Z~cOXSo(A;UrDAD%t37zmC-MU3xN<nM-@$TjtQfAl_#*Awm*mhy@cY>wOOoz9P?xNMq;Ii5Mmfwu=T>o<<jN0`5H+6>^4GjUSaubZ)?v5tCRUQx0awVPoMNH6i###4QuocD!^Yc%?p|V`WM0`w#n5lFy#MPtS!R=lhKpL`+A`h4b>~qpwCt*FHLFOM$u4NW!1h+Ko0giWrt*x{6ycclRTpov0r@f2o^ZCu?_2RBO7Dw&&k7h7>{(KlsoQ0&zPosLqqD4510#nX<@O2sedL1=-2NG!3Qa!{p2!__tCX}<{K4swkp`-eVcv>cOk4+s;M_VWDqRyEMqLUS-RgTY;yN3*H=%UqpxiZJtMjdwOgyu$Vj`7d{y&e1kVoH<^"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
