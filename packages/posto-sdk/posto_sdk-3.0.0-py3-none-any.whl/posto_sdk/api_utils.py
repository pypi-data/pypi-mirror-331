
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c$}40O>fgc5WV|XjLabpN^HR~5=f;jP$+HG25~^h+S=n}sl97<*Mtz|zcXvEo!I?Q$RSxz-kXm%Gu}+e0?el5VhOw`r802F6ElGmvGJTi;jap{(d~0CmrKHXo;{#~H?1XHqPeVXfj^hp$lJ5e{@C-9oM{aw^NZ7*qcAfM=;QnTJEqZ^A*t=K=4J(nED9+gt3+bB6fEavL)e;Af2Ei~9CN`<90wZnYyx-WD6UjK18vj<SY=kRk@qNS!?+3Pf?g1jlh?lpW_1|819gWJwbXmA{p<tPxqrR61ew)-zDbqN6;hpCXv0K;J>p?XCv>KGJYlv#sI7+?c4u2$*oGvT+heGxDqaSoXf*DFSIAOSny}kmc;Cj9ivO)c`ZLI^_&kB_KCzuY>2pq{FqG$Xu_=)#J}b-IB^~|L<fen~2Hl}Kh*6}a<ifZXmCUS~Zou@d{p~g7UB&Yh7<E0*p=DZmk7-Kd+BULdS`!2qE<^C6bvd=^Mwy<LG?l2L->;%%#e~3I`{SOk?%@VarNki8`zO;oY@4d7B=NS_z}?nnwHr=y!R|43E9SH+keZdcVQ#~@$Coef*Nh~nWwfjMy*AUj{^%+Ch1>!YwJgqivtOu`R6y0Ixn1HT^lj7mxLC~H0|Xz=7ZaFY-_kdlB<!oW&-p=DdbqY2!lfy1)*Z-D6*PAmGD@_4`GoH9AKkh^T}nY~`sw!i3Q}g+6J*9U4!B)d{F7j5Gt=QsV>@pxGq`AWztuNmJlBtogi)Km|EBIxqoE;SRc?Zj+uhNmx60!|TCSuw4}=Mt&Ny~|1>3{;V16F;8!D?sOv1<X5;K(!hPZmPJGkAe14tv*QQ`s9fPGDx>m;lPG|2qJ$+gNNjo_AsJ;3p9u(fs8p7#Pyo6F;H>a=%$bvD1gxLVwHuf<Wj{i7L-o_{}#CXONL^3$lEVYCRxC@|%$2Va-b@7GadcOZdgE!F)qiF63Z(A*&1ewlp4HI0*@rPc%Qac7@F&WgK~f%}Ipf+xainb0jcZKFq9ciKG&qLUS-RgTZpu!jsdREXxwl{tnRb=aX3no6}f#zO=2cJL3<EV6w"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
