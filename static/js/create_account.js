document.addEventListener('DOMContentLoaded', function() {
        const avatarPreview = document.getElementById('avatarPreview');
        const avatarUrlInput = document.getElementById('avatarUrl');

        const hairTypeSelect = document.querySelector('select[name="hairType"]');
        hairTypeSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const facialHairSelect = document.querySelector('select[name="facialHairType"]');
        facialHairSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const eyeTypeSelect = document.querySelector('select[name="eyeType"]');
        eyeTypeSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const eyebrowTypeSelect = document.querySelector('select[name="eyebrowType"]');
        eyebrowTypeSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const mouthTypeSelect = document.querySelector('select[name="mouthType"]');
        mouthTypeSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const skinColorSelect = document.querySelector('select[name="skinColor"]');
        skinColorSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const hairColorSelect = document.querySelector('select[name="hairColor"]');
        hairColorSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
        const clotheTypeSelect = document.querySelector('select[name="clotheType"]');
        clotheTypeSelect.addEventListener('change', function() {
            avatarPreview.src = `https://avataaars.io/?avatarStyle=Circle&topType=${hairTypeSelect.value}&accessoriesType=None&hairColor=${hairColorSelect.value}&facialHairType=${facialHairSelect.value}&facialHairColor=${hairColorSelect.value}&clotheType=${clotheTypeSelect.value}&clotheColor=Black&eyeType=${eyeTypeSelect.value}&eyebrowType=${eyebrowTypeSelect.value}&mouthType=${mouthTypeSelect.value}&skinColor=${skinColorSelect.value}`;
            avatarUrlInput.value = avatarPreview.src;
        });
    });
