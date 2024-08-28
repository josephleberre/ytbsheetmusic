//page1
const form = document.getElementById('upload-form');
const titleinput = document.getElementById('title');
const settitleinput = document.getElementById('settitle');
const colorinput = document.getElementById("color")
const numberimginput = document.getElementById("numberimg")
const numerotationinput = document.getElementById("numerotation")
const deformationinput = document.getElementById("deformation")

const cropLeftpreInput = document.getElementById('cropLeft_pre');
const cropToppreInput = document.getElementById('cropTop_pre');
const cropRightpreInput = document.getElementById('cropRight_pre');
const cropBottompreInput = document.getElementById('cropBottom_pre');


const cropLeftechInput = document.getElementById('cropLeft_ech');
const cropTopechInput = document.getElementById('cropTop_ech');
const cropRightechInput = document.getElementById('cropRight_ech');
const cropBottomechInput = document.getElementById('cropBottom_ech');

const progressBarFill = document.getElementById('progress-bar-fill');
const progressTask = document.getElementById('progress-task');
//page2
const titleinput_ = document.getElementById('title_');
const settitleinput_ = document.getElementById('settitle_');
const colorinput_ = document.getElementById("color_")
const numberimginput_ = document.getElementById("numberimg_")
const numerotationinput_ = document.getElementById("numerotation_")
const deformationinput_ = document.getElementById("deformation_")
const framescontainer = document.getElementById('framescontainer');
let frame_elements = document.getElementsByClassName('frame')

const cropLeftInput = document.getElementById('cropLeftDef');
const cropTopInput = document.getElementById('cropTopDef');
const cropRightInput = document.getElementById('cropRightDef');
const cropBottomInput = document.getElementById('cropBottomDef');

const cropLeftInputDef = document.getElementById('cropLeft_def');
const cropTopInputDef = document.getElementById('cropTop_def');
const cropRightInputDef = document.getElementById('cropRight_def');
const cropBottomInputDef = document.getElementById('cropBottom_def');

const downloadButtons = document.getElementById('download-buttons');
const pdfDownload = document.getElementById('pdf-download');
const mp3Download = document.getElementById('mp3-download');
const zipDownload = document.getElementById('zip-download');
const pdfviewer = document.getElementById('pdfviewer');
//variable
let selectedFrameIds = []
let cropper_value = [0, 0, 0, 0]
let page = 1

//MENU DEROULANT FORM

document.addEventListener('DOMContentLoaded', function () {
    const dropdownHeader = document.getElementById('dropdownHeader');
    const dropdownContent = document.getElementById('dropdownContent');
    const dropdownHeader_ = document.getElementById('dropdownHeader_');
    const dropdownContent_ = document.getElementById('dropdownContent_');

    dropdownHeader_.addEventListener('click', function () {
        dropdownContent_.classList.toggle('show');
        dropdownHeader_.querySelector('.chevron').classList.toggle('show');
    });

    dropdownHeader.addEventListener('click', function () {
        dropdownContent.classList.toggle('show');
        dropdownHeader.querySelector('.chevron').classList.toggle('show');
    });

    window.addEventListener('click', function (event) {
        if (!dropdownHeader.contains(event.target) && !dropdownContent.contains(event.target)) {
            dropdownContent.classList.remove('show');
            dropdownHeader.querySelector('.chevron').classList.remove('show');
        }
        if (!dropdownHeader_.contains(event.target) && !dropdownContent_.contains(event.target)) {
            dropdownContent_.classList.remove('show');
            dropdownHeader_.querySelector('.chevron').classList.remove('show');
        }
    });
});

//CHANGEMENT DE PAGE

function changePage() {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.toggle('active'));
    if(page == 1){
        titleinput_.value = titleinput.value
        settitleinput_.checked = settitleinput.checked
        colorinput_.value =  colorinput.value
        numberimginput_.value = numberimginput.value
        numerotationinput_.checked = numerotationinput.checked
        deformationinput_.checked = deformationinput.checked
        cropLeftInputDef.value = cropLeftpreInput.value
        cropTopInputDef.value = cropToppreInput.value
        cropRightInputDef.value = cropRightpreInput.value
        cropBottomInputDef.value = cropBottompreInput.value
        page +=1
    }else{
        titleinput.value = titleinput_.value
        settitleinput.checked = settitleinput_.checked
        colorinput.value =  colorinput_.value
        numberimginput.value = numberimginput_.value
        numerotationinput.checked = numerotationinput_.checked
        deformationinput.checked = deformationinput_.checked
        cropLeftpreInput.value = cropLeftInputDef.value
        cropToppreInput.value = cropTopInputDef.value
        cropRightpreInput.value = cropRightInputDef.value
        cropBottompreInput.value = cropBottomInputDef.value
        page -=1
    }
}

//GESTION DE LA PROGRESS BAR

const messages = [
    { min: 0, max: 5, text: 'Création du dossier' },
    { min: 5, max: 20, text: 'Récupération de la vidéo...' },
    { min: 20, max: 40, text: 'Baisse du framerate...' },
    { min: 40, max: 80, text: 'Analyse des images...' },
    { min: 80, max: 90, text: 'Traitement et création du pdf' },
    { min: 90, max: 100, text: "Récupération de l'audio..." },
];

function getMessageForPercentage(percent) {
    for (const message of messages) {
        if (percent >= message.min && percent < message.max) {
            return message.text;
        }
    }
    return 'En attente...'; // Message par défaut
}

//GESTION DES FRAMES 

function toggleFrameSelection(event) {
    const frame = event.target;
    const frameId = frame.getAttribute('id');
    frame.classList.toggle('selected');
    selectedFrameIds = []

    for (let i = 0; i < frame_elements.length; i++) {
        if (!frame_elements[i].classList.contains('selected')) {
            selectedFrameIds.push(parseInt(frame_elements[i].id));
        }
    }

    selectedFrameIds.sort()
    actualise_pdf()
}

function attachClickEventToFrames() {
    for (let i = 0; i < frame_elements.length; i++) {
        frame_elements[i].addEventListener('click', toggleFrameSelection);
    }
}

//TRAITEMENT DU FORMULAIRE

form.onsubmit = function(event) {
    event.preventDefault();

    progressBarFill.style.width = '0%';
    progressBarFill.textContent = '0%';
    progressTask.textContent = 'En attente...';
    downloadButtons.style.display = 'none';

    cropper_value = [cropLeftpreInput.value, cropToppreInput.value,cropRightpreInput.value,cropBottompreInput.value]

    var title = titleinput.value;
    const formData = new FormData(form);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/traitement/", true);

    // Gestion de la progression
    xhr.onprogress = function(event) {
        if (event.lengthComputable) {
            var percentComplete = (event.loaded / event.total) * 100;
            progressBarFill.style.width = `${percentComplete}%`;
            progressBarFill.textContent = `${Math.floor(percentComplete)}%`;
            progressTask.textContent = getMessageForPercentage(percentComplete);
        }
    };

    // Gestion des mises à jour de progression et du JSON
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.LOADING) {
            const responseText = xhr.responseText;
            const progressMatch = responseText.match(/data: (\d+)/g);
            if (progressMatch) {
                var latestProgress = progressMatch[progressMatch.length - 1].split(' ')[1];
                progressBarFill.style.width = `${latestProgress}%`;
                progressBarFill.textContent = `${latestProgress}%`;
                progressTask.textContent = getMessageForPercentage(latestProgress);
            }
            if(responseText.match(/frames: (\d+)/g) && progressMatch.length == 4){
                const frames = responseText.match(/frames: (\d+)/g);
                const frames_nbr = frames[frames.length - 1].split(' ')[1];
                selectedFrameIds = [];
                framescontainer.innerHTML = "";
                for (let step = 0; step < frames_nbr; step++) {
                    const timestamp = new Date().getTime();
                    const e = document.createElement("img");
                    e.classList.add('frame')
                    e.setAttribute('id', step)
                    e.src = `/img/${step}?ts=${timestamp}`;
                    framescontainer.appendChild(e);
                    selectedFrameIds.push(step)
                }
                frame_elements = document.getElementsByClassName('frame');
                attachClickEventToFrames();
            }
        };

        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                progressBarFill.style.width = '100%';
                progressBarFill.textContent = 'Traitement terminé !';
                progressTask.textContent = 'Traitement terminé !';
                const timestamp = new Date().getTime();
                pdfviewer.src = `/pdf/?ts=${timestamp}`;
                downloadButtons.style.display = 'block';
                changePage()
                if(!document.getElementsByClassName("back-button")[1]){
                    const e = document.createElement("div");
                    e.classList.add('back-button')
                    e.classList.add('right')
                    e.setAttribute('id', "backButton")
                    e.setAttribute('onClick', "changePage()")
                    e.innerHTML = 'Retour'
                    form.prepend(e)
                }
            } else {
                progressBarFill.style.backgroundColor = 'red';
                progressBarFill.textContent = 'Erreur!';
                progressTask.textContent = 'Erreur!';
            }
        }
    };

    xhr.send(formData);
};

//ACTUALISER LE PDF
function actualise_pdf(){
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/changepdf", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    const data = {
        cropper_value: cropper_value,
        frames: selectedFrameIds,
        title: titleinput_.value,
        settitle: settitleinput_ .checked,
        color: colorinput_.value,
        numberimg: numberimginput_.value,
        numerotation: numerotationinput_.checked,
        deformation: deformationinput_.checked
    };
    
    xhr.send(JSON.stringify(data));

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            const timestamp = new Date().getTime();
            document.getElementById('pdfviewer').src = `/pdf/?ts=${timestamp}`;
        } else {
            console.error("Request failed");
        }
    };

    xhr.onerror = function() {
        console.error("Request error");
    };
}

function downloadFrames() {
    fetch('/download/frames', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedFrameIds: selectedFrameIds, color: colorinput_.value, cropper_value: cropper_value })
    })
    .then(response => {
        const filename = response.headers.get('Content-Disposition')
            .split('filename=')[1].replace(/"/g, '');
        return response.blob().then(blob => ({ blob, filename }));
    })
    .then(({ blob, filename }) => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(a.href);
    })
    .catch(console.error);
}



document.addEventListener('DOMContentLoaded', function () {
    function initializeCropper(modalId, imageId, cropButtonId, closeButtonClass, inputs) {
        let cropper;
        const modal = document.getElementById(modalId);
        const img = document.getElementById(imageId);
        const cropButton = document.getElementById(cropButtonId);
        const closeModal = document.getElementById(closeButtonClass);

        document.getElementById(`open${modalId}`).onclick = function() {
            modal.style.display = 'flex';

            const videoUrl = document.getElementById('url').value;
            const title = titleinput.value
            if (videoUrl) {
                img.src = "/static/img/wait.png"
                fetch('/generate-thumbnail', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: videoUrl, title: title }),
                })
                .then(response => response.json())
                .then(data => {
                    img.src = data.thumbnailUrl
                    cropper = new Cropper(img, {
                        aspectRatio: NaN,
                        viewMode: 3,
                        autoCropArea: 1.0,
                        movable: false,
                        zoomable: true,
                        scalable: true,
                        cropBoxResizable: true,
                        cropBoxMovable: true,
                        dragMode: 'move',
                        minContainerWidth: 0,
                        minContainerHeight: 0,
                        ready: function () {
                            const cropData = {
                                x: parseFloat(inputs.leftInput.value) || 0,
                                y: parseFloat(inputs.topInput.value) || 0,
                                width: parseFloat(img.width - inputs.leftInput.value - inputs.rightInput.value) || 0,
                                height: parseFloat(img.height - inputs.topInput.value - inputs.bottomInput.value) || 0
                            };
                            cropper.setData(cropData);
                            inputs.left.value = cropData.x;
                            inputs.top.value = cropData.y;
                            inputs.right.value = img.width - cropData.width - cropData.x;
                            inputs.bottom.value = img.height - cropData.height - cropData.y;
                        }
                    });
                });
            } else {
                img.src = "/static/img/add_url.png"
                cropper = new Cropper(img, {
                    aspectRatio: NaN,
                    viewMode: 3,
                    autoCropArea: 1.0,
                    movable: false,
                    zoomable: true,
                    scalable: true,
                    cropBoxResizable: true,
                    cropBoxMovable: true,
                    dragMode: 'move',
                    minContainerWidth: 0,
                    minContainerHeight: 0,
                    ready: function () {
                        const cropData = {
                            x: parseFloat(inputs.leftInput.value) || 0,
                            y: parseFloat(inputs.topInput.value) || 0,
                            width: parseFloat(img.width - inputs.leftInput.value - inputs.rightInput.value) || 0,
                            height: parseFloat(img.height - inputs.topInput.value - inputs.bottomInput.value) || 0
                        };
                        cropper.setData(cropData);
                        inputs.left.value = cropData.x;
                        inputs.top.value = cropData.y;
                        inputs.right.value = img.width - cropData.width - cropData.x;
                        inputs.bottom.value = img.height - cropData.height - cropData.y;
                    }
                });
            }
        };

        function updateCropper() {
            const cropData = {
                x: parseFloat(inputs.left.value) || 0,
                y: parseFloat(inputs.top.value) || 0,
                width: parseFloat(img.width - inputs.left.value - inputs.right.value) || 0,
                height: parseFloat(img.height - inputs.top.value - inputs.bottom.value) || 0
            };
            cropper.setData(cropData);
        }

        inputs.left.addEventListener('input', updateCropper);
        inputs.top.addEventListener('input', updateCropper);
        inputs.right.addEventListener('input', updateCropper);
        inputs.bottom.addEventListener('input', updateCropper);

        img.addEventListener('crop', function(event) {
            const cropData = cropper.getData();
            inputs.left.value = Math.round(cropData.x);
            inputs.top.value = Math.round(cropData.y);
            inputs.right.value = Math.round(img.width - (cropData.x + cropData.width));
            inputs.bottom.value = Math.round(img.height - cropData.height - cropData.y);
        });

        cropButton.onclick = function() {
            modal.style.display = 'none';
            if (modalId === "cropModalDef") {
                inputs.leftInput.value = cropper_value[0] = inputs.left.value;
                inputs.topInput.value = cropper_value[1] = inputs.top.value;
                inputs.rightInput.value = cropper_value[2] = inputs.right.value;
                inputs.bottomInput.value = cropper_value[3] = inputs.bottom.value;
                actualise_pdf();
            } else {
                inputs.leftInput.value = inputs.left.value;
                inputs.topInput.value = inputs.top.value;
                inputs.rightInput.value = inputs.right.value;
                inputs.bottomInput.value = inputs.bottom.value;
            }
            cropper.destroy();
        };

        closeModal.onclick = function() {
            modal.style.display = 'none';
            cropper.destroy();
        };

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
                cropper.destroy();
            }
        };
    }

    initializeCropper('cropModalDef', 'imageToCropDef', 'cropButtonDef', 'closeDef', {
        left: document.getElementById('cropLeftDef'),
        top: document.getElementById('cropTopDef'),
        right: document.getElementById('cropRightDef'),
        bottom: document.getElementById('cropBottomDef'),
        leftInput: document.getElementById('cropLeft_def'),
        topInput: document.getElementById('cropTop_def'),
        rightInput: document.getElementById('cropRight_def'),
        bottomInput: document.getElementById('cropBottom_def')
    });

    initializeCropper('cropModalPre', 'imageToCropPre', 'cropButtonPre', 'closePre', {
        left: document.getElementById('cropLeftPre'),
        top: document.getElementById('cropTopPre'),
        right: document.getElementById('cropRightPre'),
        bottom: document.getElementById('cropBottomPre'),
        leftInput: document.getElementById('cropLeft_pre'),
        topInput: document.getElementById('cropTop_pre'),
        rightInput: document.getElementById('cropRight_pre'),
        bottomInput: document.getElementById('cropBottom_pre')
    });

    initializeCropper('cropModalEch', 'imageToCropEch', 'cropButtonEch', 'closeEch', {
        left: document.getElementById('cropLeftEch'),
        top: document.getElementById('cropTopEch'),
        right: document.getElementById('cropRightEch'),
        bottom: document.getElementById('cropBottomEch'),
        leftInput: document.getElementById('cropLeft_ech'),
        topInput: document.getElementById('cropTop_ech'),
        rightInput: document.getElementById('cropRight_ech'),
        bottomInput: document.getElementById('cropBottom_ech')
    });
});