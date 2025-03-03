
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c$~#pUys{141dq35Ihu)0VmgP0}2GV0R=8Cie1~o?lxcu0z+rZiCWvrB>B=qao>HU<Uf+_+|un~d9Y=X{D~qdl1eT`N%Z4^S3APXgOHkBbERW)#Z!2`sUBnU>7co&Xc3d&D;Ugjl*y=OnwPAVYQJNG&x{qC&Kgo7c00hI&2YdZxol^aJEpJA+&s7uN{id8UxR2iOAD$LxlQ*hs|)slRuouPGXlRL2<*2av?z#bcovcspg=~%fk}$$D&RB{=8>_SBnhv$PLjD|MIIA+;7M9=R_Vw>;}1#81W2G{&(M)OtO9J*;B-U_psB9as<YX~m~5l8jE!M&wB2q2{-dZ^><d>+ABFt#FQpG)l@;NY2J)*RjmgBLzZ@{MhD><oEDy{l7TZZtAADxitznMH;ujM^R&|J?ZEs_6%sZwDHAW;N@77l2$n_pvXaPyi3(X|PiSGdXy^%Y$@>FUq|JF#6`^RR6%tI!nkYP;1O6Wv^Lval646x0xPE)274l_w}9Y!8<=N1QAq#QJCD0AftSWDl)lT>wi4<fmcILj*&n?7^rnva$jEW$M_6;ce8zfIRsjzR~P@|>p~oxH#D<a&oWLM^W$x)SZ-vAdBJw7DeTJiriD3s*)%KR7}ujw(q-4TfHI`|DVq#@^(4>pl+%rn%x3kgAl;Ek_KTGV=L)_k)%jJK7FBf_vD6mc~?wks8L~^0VMogY5gz)vXPHXOwGLPHESWQN3n(LO&B%Ny9Txvza}uryCp7@I8ZpcD_%7c7gLeV#{W5+mC5b$#gBNKG!ajl73-{WPjBR(rWl_eTPT!;&@nmR-(Gd)#3ovfys-9R~KEf02ZsnrF}(ywueRJW0RsgnU$?znAe(wiWzSEPwDD6#3DK61yq<0?7XbhFMSKy2F{vuKnY}pVG@LCMYOQ`PoBrYsc097F||i0RyXIO{n$>s1u8hjQyxNf2H&a87EW&`^mMlSZa&?f<G%~DLtw;pFYz((AoLJSGwZ^^fpX&3t+l;Jr;8S0U(=$_zFX`+6?Gzt3{s%p(`vd{4*8+4S&@4o3ZTEGg|gKYC%mA%GUjnyTvDCxv5(Vx$mslmRV0-hD=7W0P_@>%ZsT&Iu$Ta~?(q;j^Io3_?1qWhE)qe86|pt<Xosdf(0i^L7Ej7G^GMPV2@<XRoGo`t628tbP=EY+kFTFzmV?4?Jn=p!cd~}Q)^6BqI~}77u)6FFe(K;t17ZMZm6@??^M2Bnvi8&2n5UhjTru(oEo!#L24^08sKMmcVUOgvr@HqO)L|(ec*eXXW6~DYevufnl43^BOWb*IqTsao!lMSfvM~VC!3r_rX*#SPto;4Mx|{8Q-3cjRcfKaMZO4e5-}-#@fAkw@n@!lL6K>na!xr6f?7E7ba`z9=P)cyPxpaX}5OfNv#}`I|*I5vg0Kynw5XONgSi`LcmhEvji&xuaA&zkE@?8u0c)ZaE3^0&~1UYvwRsa%>m_dKL9JDQ2I0iGe!Mh;<cK5`2MjzFsS!ayM3Kw&KHs)T`@=Vb3Y|xTdwPw%2DmD!@KC5@=Mx#QBr}mzq!H6+M6yrvT-9lu}Bj`xl)uUj%GX6%BqaaKr!%K2<&)`17Ofb&dd;78y$2n9QyX$BP5tifpJbdxz;zhZ5kqwd~oJDrf&YlQWWMccHt>?k}3Jl0ICnWKL1gUgM)?aCPC?H*pb2AW89?mxCHfPb3V~1`q3gMG&%GLUMeYZZZ(L}1#qI6rcoe(C;ZoV<g+Pt8$O<2YL4YFj7HQw63vP;!&&p5GFXJOMFkiP+64h(G"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
