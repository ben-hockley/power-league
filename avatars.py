import random
import python_avatars as pa

def random_football_avatar(filename="football_avatar.svg"):
    # Define likely football player features
    hair_types = [
        pa.HairType.SHORT_FLAT, pa.HairType.SHORT_ROUND, pa.HairType.SHORT_WAVED, pa.HairType.DREADS, pa.HairType.NONE, pa.HairType.BUZZCUT
    ]
    eyebrow_types = [
        pa.EyebrowType.DEFAULT_NATURAL, pa.EyebrowType.DEFAULT, pa.EyebrowType.ANGRY,
    ]
    eye_types = [
        pa.EyeType.DEFAULT, pa.EyeType.SQUINT, pa.EyeType.DEFAULT
    ]
    nose_types = [
        pa.NoseType.DEFAULT, pa.NoseType.SMALL, pa.NoseType.WIDE
    ]
    mouth_types = [
        pa.MouthType.SERIOUS, pa.MouthType.DEFAULT
    ]
    facial_hair_types = [
        pa.FacialHairType.NONE, pa.FacialHairType.BEARD_LIGHT, pa.FacialHairType.BEARD_MEDIUM, pa.FacialHairType.MOUSTACHE_MAGNUM, pa.FacialHairType.NONE, pa.FacialHairType.NONE, pa.FacialHairType.NONE, pa.FacialHairType.NONE, 
    ]
    hair_colors = [
        pa.HairColor.BLACK, pa.HairColor.BROWN, pa.HairColor.BLONDE, pa.HairColor.BROWN
    ]
    skin_colors = [
        pa.SkinColor.LIGHT, pa.SkinColor.BLACK, pa.SkinColor.DARK_BROWN, pa.SkinColor.TANNED, pa.SkinColor.BROWN, pa.SkinColor.BLACK, pa.SkinColor.BLACK, pa.SkinColor.BLACK
    ]
    clothing_types = [
        pa.ClothingType.SHIRT_CREW_NECK
    ]
    clothing_colors = [
        pa.ClothingColor.WHITE
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
        skin_color=random.choice(skin_colors),
        hair_color=random.choice(hair_colors),
        accessory=pa.AccessoryType.NONE,
        clothing=random.choice(clothing_types),
        clothing_color=random.choice(clothing_colors)
    )
    avatar.render(filename)

# Example usage:
random_football_avatar("random_football_player.svg")