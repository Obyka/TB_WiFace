import py_avataaars as pa
import pictures
import config
from decimal import *
import os

# Tous les choix dependant du genre sont arbitraires et ont uniquement une valeur de différentiation statistique.
def draw_avatar(base_picture):

    name, ext = os.path.splitext(base_picture['picPath'])
    avatar_name = "{name}_avatar.png".format(name=name)
    avatar_path = os.path.join(config.app.config['UPLOAD_FOLDER'], avatar_name)

    if(os.path.exists(avatar_path)):
        return avatar_name
    emotions = ['happy', 'surprised', 'fear', 'confused', 'sad', 'calm', 'disgusted', 'angry']
    options_accessory = ['eyeglasses', 'sunglasses']
    options_facial_hair = ['beard', 'mustache']
    main_emotion = sorted([(emotion, base_picture.get(emotion)) for count, emotion in enumerate(emotions) if base_picture.get(emotion) and abs(base_picture.get(emotion)) >= 1], key=lambda emotion: emotion[1], reverse=True)[0]

    top = pa.TopType.LONG_HAIR_STRAIGHT if base_picture['gender'] > 0 else pa.TopType.SHORT_HAIR_SHORT_FLAT

    #https://www.independent.co.uk/life-style/hair-colour-men-women-blonde-black-genetic-roots-dna-study-a8308301.html

    facial_hair_color = pa.FacialHairColor.BLONDE_GOLDEN if base_picture['gender'] > 0 else pa.FacialHairColor.BROWN_DARK
    hair_color = pa.HairColor.BLONDE_GOLDEN if base_picture['gender'] > 0 else pa.HairColor.BROWN_DARK

    options_eyes = {
        'happy' : pa.EyesType.HAPPY,
        'surprised' : pa.EyesType.SURPRISED,
        'fear' : pa.EyesType.SURPRISED,
        'confused' : pa.EyesType.DEFAULT,
        'sad' : pa.EyesType.CRY,
        'calm' :pa.EyesType.DEFAULT,
        'disgusted' : pa.EyesType.DIZZY,
        'angry' : pa.EyesType.SQUINT
    }

    options_eyebrow = {
        'happy' : pa.EyebrowType.DEFAULT_NATURAL,
        'surprised' : pa.EyebrowType.RAISED_EXCITED_NATURAL,
        'fear' : pa.EyebrowType.RAISED_EXCITED_NATURAL,
        'confused' : pa.EyebrowType.FROWN_NATURAL,
        'sad' : pa.EyebrowType.SAD_CONCERNED_NATURAL,
        'calm' :pa.EyebrowType.DEFAULT_NATURAL,
        'disgusted' : pa.EyebrowType.FROWN_NATURAL ,
        'angry' : pa.EyebrowType.ANGRY_NATURAL 
    }
    options_mouth = {
        'happy' : pa.MouthType.SMILE,
        'surprised' : pa.MouthType.SCREAM_OPEN,
        'fear' : pa.MouthType.SCREAM_OPEN,
        'confused' : pa.MouthType.CONCERNED,
        'sad' : pa.MouthType.SAD,
        'calm' : pa.MouthType.DEFAULT,
        'disgusted' : pa.MouthType.GRIMACE,
        'angry' : pa.MouthType.DISBELIEF
     }

    options_accessory = {
        'sunglasses':pa.AccessoriesType.SUNGLASSES,
        'eyeglasses':pa.AccessoriesType.PRESCRIPTION_01
    }

    options_facial_hair = {
        'beard':pa.FacialHairType.BEARD_LIGHT,
        'mustache':pa.FacialHairType.MOUSTACHE_MAGNUM
    }

    max_accessory = max(options_accessory, key = lambda k: base_picture[k])
    if base_picture[max_accessory] < 0:
        accessory = pa.AccessoriesType.DEFAULT
    else:
        accessory = options_accessory[max_accessory]

    max_facial_hair = max(options_facial_hair, key = lambda k: base_picture[k])
    if base_picture[max_facial_hair] < 0:
        facial_hair = pa.FacialHairType.DEFAULT
    else:
        facial_hair = options_facial_hair[max_facial_hair]

    avatar = pa.PyAvataaar(
        style=pa.AvatarStyle.TRANSPARENT,
        skin_color=pa.SkinColor.YELLOW,
        hair_color=hair_color,
        facial_hair_type=facial_hair,
        facial_hair_color=facial_hair_color,
        top_type=top,
        hat_color=pa.ClotheColor.BLACK,
        mouth_type=options_mouth[main_emotion[0]],
        eye_type=options_eyes[main_emotion[0]],
        eyebrow_type=options_eyebrow[main_emotion[0]],
        accessories_type=accessory,
        clothe_type=pa.ClotheType.SHIRT_CREW_NECK,
        clothe_color=pa.ClotheColor.HEATHER,
        clothe_graphic_type=pa.ClotheGraphicType.BAT,
    )
    
    avatar.render_png_file(avatar_path)
    return avatar_name
