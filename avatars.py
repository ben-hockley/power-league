import random
import python_avatars as pa

def random_football_avatar(player_id: int):
    hair_types = [
        pa.HairType.CAESAR,
        pa.HairType.CAESAR_SIDE_PART,
        pa.HairType.CORNROWS,
        pa.HairType.SHORT_DREADS_1,
        pa.HairType.SHORT_DREADS_2,
        pa.HairType.SHORT_ROUND,
        pa.HairType.DREADS,
        pa.HairType.NONE,
        pa.HairType.BUZZCUT,
        pa.HairType.SHORT_FLAT,
        pa.HairType.BUN,
        pa.HairType.SHORT_WAVED,
        pa.HairType.MOHAWK
    ]
    eyebrow_types = [
        pa.EyebrowType.DEFAULT_NATURAL, pa.EyebrowType.DEFAULT,
        pa.EyebrowType.DEFAULT_NATURAL, pa.EyebrowType.DEFAULT,
        pa.EyebrowType.ANGRY, pa.EyebrowType.ANGRY_NATURAL
    ]
    eye_types = [
        pa.EyeType.DEFAULT, pa.EyeType.SQUINT, pa.EyeType.DEFAULT, pa.EyeType.SIDE
    ]
    nose_types = [
        pa.NoseType.DEFAULT, pa.NoseType.SMALL, pa.NoseType.WIDE
    ]
    mouth_types = [
        pa.MouthType.SERIOUS, pa.MouthType.DEFAULT, pa.MouthType.TWINKLE, pa.MouthType.SMILE
    ]
    facial_hair_types = [
        pa.FacialHairType.NONE, pa.FacialHairType.NONE, pa.FacialHairType.NONE,
        pa.FacialHairType.BEARD_LIGHT, pa.FacialHairType.BEARD_MEDIUM, 
        pa.FacialHairType.BEARD_LIGHT, pa.FacialHairType.BEARD_LIGHT,
        pa.FacialHairType.WICK_BEARD, pa.FacialHairType.MOUSTACHE_FANCY, pa.FacialHairType.MOUSTACHE_MAGNUM
    ]
    hair_colors = [
        pa.HairColor.BLACK, pa.HairColor.BLACK, pa.HairColor.BLACK, pa.HairColor.BLACK, pa.HairColor.BLACK,
        pa.HairColor.BROWN_DARK, pa.HairColor.BROWN_DARK, pa.HairColor.BROWN_DARK,
        pa.HairColor.BROWN, pa.HairColor.BLONDE
    ]
    skin_colors = [
        pa.SkinColor.PALE, pa.SkinColor.PALE,
        pa.SkinColor.LIGHT, pa.SkinColor.TANNED, pa.SkinColor.BROWN, pa.SkinColor.DARK_BROWN,
        pa.SkinColor.BLACK, pa.SkinColor.BLACK, pa.SkinColor.BLACK, pa.SkinColor.BLACK, pa.SkinColor.BLACK
    ]
    clothing_types = [
        pa.ClothingType.SHIRT_CREW_NECK
    ]
    clothing_colors = [
        pa.ClothingColor.BLACK
    ]

    avatar = pa.Avatar(
        style=pa.AvatarStyle.CIRCLE,
        background_color=random.choice(list(pa.BackgroundColor)),
        top=random.choice(hair_types),
        eyebrows=random.choice(eyebrow_types),
        eyes=random.choice(eye_types),
        nose=random.choice(nose_types),
        mouth=random.choice(mouth_types),
        facial_hair=random.choice(facial_hair_types),
        facial_hair_color=pa.HairColor.BLACK,
        skin_color=random.choice(skin_colors),
        hair_color=random.choice(hair_colors),
        accessory=pa.AccessoryType.NONE,
        clothing=random.choice(clothing_types),
        clothing_color=random.choice(clothing_colors)
    )
    avatar.render("static/avatars/" + str(player_id) + ".svg")

