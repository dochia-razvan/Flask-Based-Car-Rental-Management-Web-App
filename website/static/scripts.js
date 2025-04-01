var dropdown = document.querySelector('.dropdown');
var dropdownContent = document.querySelector('.dropdown-content');
var dropdownBtn = document.querySelector('.dropdown-btn');

if (dropdownBtn) {
        dropdownBtn.addEventListener('click', function (event) {
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
        event.stopPropagation();
    });

    dropdown.addEventListener('mouseleave', function () {
        dropdownContent.style.display = 'none';
    });

    document.addEventListener('click', function (event) {
        if (!dropdown.contains(event.target)) {
            dropdownContent.style.display = 'none';
        }
    });
}

const marcaDropdown = document.getElementById('id_marca');
const modeleDropdown = document.getElementById('id_model');

if (marcaDropdown) {
    marcaDropdown.selectedIndex = 0;
}

if (modeleDropdown) {
    modeleDropdown.disabled = true;
    modeleDropdown.innerHTML = '<option value="" disabled selected>Selectează Marca întâi</option>';
}

if (modeleDropdown) {
    modeleDropdown.disabled = true;
    modeleDropdown.innerHTML = '<option value="" disabled selected>Selectează Marca întâi</option>';
}

if (marcaDropdown && modeleDropdown) {
    marcaDropdown.addEventListener('change', function () {
        const marcaId = this.value;

        if (marcaId) {
            modeleDropdown.disabled = false;
            fetch(`/get-models/${marcaId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    modeleDropdown.innerHTML = '<option value="" disabled selected>Selectează Model</option>';

                    if (data.modele.length > 0) {
                        data.modele.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model.id;
                            option.textContent = model.denumire;
                            modeleDropdown.appendChild(option);
                        });
                    } else {
                        modeleDropdown.innerHTML = '<option value="" disabled selected>Nu există modele disponibile</option>';
                        modeleDropdown.disabled = true;
                    }
                })
                .catch(error => {
                    console.error('Error fetching models:', error);
                    modeleDropdown.innerHTML = '<option value="" disabled selected>Eroare la încărcarea modelelor</option>';
                    modeleDropdown.disabled = true;
                });

        } else {
            modeleDropdown.disabled = true;
            modeleDropdown.innerHTML = '<option value="" disabled selected>Selectează Marca întâi</option>';
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const successPopup = document.getElementById("successPopup");

    if (successPopup) {
        setTimeout(() => {
            successPopup.style.opacity = "0";
            setTimeout(() => {
                successPopup.style.display = "none";
            }, 1000);
        }, 5000);

        const url = new URL(window.location);
        if (url.searchParams.has("success_message")) {
            url.searchParams.delete("success_message");
            window.history.replaceState({}, document.title, url.toString());
        }
    }
});

const url = new URL(window.location);
if (url.searchParams.has("errors")) {
    url.searchParams.delete("errors");
    window.history.replaceState({}, document.title, url.toString());
}

document.addEventListener("DOMContentLoaded", () => {
    const rezervareButtons = document.querySelectorAll(".rezerva2-btn");
    const confirmButton = document.querySelector(".rezerva-confirmare-btn");
    const selectedMasini = new Set();

    rezervareButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const masinaId = button.dataset.masinaId;

            if (selectedMasini.has(masinaId)) {
                selectedMasini.delete(masinaId);
                button.textContent = "Rezervă";
                button.classList.remove("anuleaza-btn");
            } else {
                selectedMasini.add(masinaId);
                button.textContent = "Anulează";
                button.classList.add("anuleaza-btn");
            }

            confirmButton.style.display = selectedMasini.size > 0 ? "block" : "none";

            const urlParams = new URLSearchParams();
            selectedMasini.forEach((id) => urlParams.append("masini_ids", id));
            confirmButton.href = `/rezervare?${urlParams.toString()}`;
        });
    });

    window.addEventListener("beforeunload", () => {
        selectedMasini.clear();
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const dataInchiriere = document.getElementById("data_inchiriere");
    const dataReturnare = document.getElementById("data_returnare");
    const totalPlataElement = document.getElementById("total_plata");

    if (dataInchiriere) {
        const today = new Date().toISOString().split("T")[0];
        dataInchiriere.setAttribute("min", today);

        window.updateReturnDate = () => {
            const inchiriereValue = dataInchiriere.value;
            if (inchiriereValue) {
                const inchiriereDate = new Date(inchiriereValue);
                inchiriereDate.setDate(inchiriereDate.getDate() + 1);
                if (dataReturnare) {
                    dataReturnare.disabled = false;
                    dataReturnare.min = inchiriereDate.toISOString().split("T")[0];
                    dataReturnare.value = "";
                }
            } else if (dataReturnare) {
                dataReturnare.disabled = true;
                dataReturnare.value = "";
            }
        };

        dataInchiriere.addEventListener("change", () => {
            window.updateReturnDate();
            calculateTotal();
        });

        if (dataReturnare) {
            dataReturnare.addEventListener("change", calculateTotal);
        }
    }

    if (dataInchiriere && dataReturnare && totalPlataElement) {
        calculateTotal();
    }
});

function calculateTotal() {
    const dataInchiriere = document.getElementById("data_inchiriere")?.value;
    const dataReturnare = document.getElementById("data_returnare")?.value;
    const masini = [...document.querySelectorAll('input[name="masini_ids"]')];
    const totalPlataElement = document.getElementById("total_plata");

    if (dataInchiriere && dataReturnare && totalPlataElement) {
        const date1 = new Date(dataInchiriere);
        const date2 = new Date(dataReturnare);
        const days = Math.ceil((date2 - date1) / (1000 * 60 * 60 * 24));

        if (days > 0) {
            const totalPlata = masini.reduce((sum, masina) => {
                const tarif = parseFloat(masina.dataset.tarif || 0);
                return sum + tarif * days;
            }, 0);

            totalPlataElement.textContent = `${totalPlata.toFixed(2)} RON`;
        } else {
            totalPlataElement.textContent = "(Data returnare trebuie să fie după data închiriere)";
        }
    } else if (totalPlataElement) {
        totalPlataElement.textContent = "(Introdu datele de închiriere)";
    } else {
        console.log("Elementul 'totalPlataElement' nu a fost găsit în DOM.");
    }
}

function toggleEditMode() {
    const editToggleBtn = document.getElementById("edit-toggle-btn");
    const editMode = editToggleBtn.classList.contains("active");
    const url = new URL(window.location);
    url.searchParams.set("edit_mode", !editMode);
    window.location.href = url.toString();
}

function showDeactivateModal(masinaId) {
    const modal = document.getElementById("deactivate-modal");
    const message = document.getElementById("deactivate-message");
    const confirmBtn = document.getElementById("modal-confirm-btn");

    message.textContent = `Ești sigur că vrei să dezactivezi mașina?`;
    modal.style.display = "block";

    confirmBtn.onclick = () => {
        deactivateMasina(masinaId);
        closeModal();
    };
}


document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("deactivate-modal");
    const overlay = document.querySelector(".modal-overlay");
    const cancelBtn = document.getElementById("modal-cancel-btn");
    const confirmBtn = document.getElementById("modal-confirm-btn");
    const modalContent = document.querySelector(".modal-content");

    if (overlay) {
        overlay.addEventListener("click", closeModal);
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", closeModal);
    }

    if (modalContent) {
        modalContent.addEventListener("click", (event) => {
            event.stopPropagation();
        });
    }

    window.showDeactivateModal = (masinaId) => {
        const message = document.getElementById("deactivate-message");
        message.textContent = `Ești sigur că vrei să dezactivezi mașina?`;
        modal.style.display = "block";

        confirmBtn.onclick = () => {
            deactivateMasina(masinaId);
            closeModal();
        };
    };

    window.showActivateModal = (masinaId) => {
        const message = document.getElementById("deactivate-message");
        message.textContent = `Ești sigur că vrei să activezi mașina?`;
        modal.style.display = "block";

        confirmBtn.onclick = () => {
            activateMasina(masinaId);
            closeModal();
        };
    };

    function closeModal() {
        modal.style.display = "none";
    }

    function deactivateMasina(masinaId) {
        fetch(`/delete-masina/${masinaId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        })
            .then((response) => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("Eroare la dezactivarea mașinii!");
                }
            })
            .catch((error) => console.error("Eroare:", error));
    }

    function activateMasina(masinaId) {
        fetch(`/activate-masina/${masinaId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        })
            .then((response) => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("Eroare la activarea mașinii!");
                }
            })
            .catch((error) => console.error("Eroare:", error));
    }
});



function deactivateMasina(masinaId) {
    fetch(`/delete-masina/${masinaId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    })
        .then((response) => {
            if (response.ok) {
                location.reload();
            } else {
                alert("Eroare la dezactivarea mașinii!");
            }
        })
        .catch((error) => console.error("Eroare:", error));
}


const selectedMasini = new Set();

document.addEventListener("DOMContentLoaded", () => {
    const marcaDropdown = document.getElementById("filter-marca");
    const modelDropdown = document.getElementById("filter-model");
    const anFabricatieInput = document.getElementById("filter-an-fabricatie");
    const tarifMaximInput = document.getElementById("filter-tarif-maxim");
    const orasDropdown = document.getElementById("filter-oras");
    const sortDropdown = document.getElementById("sort-status-dropdown");
    const masiniContainer = document.querySelector(".masini-container");
    const anErrorMessage = document.getElementById("error-message-an");
    const tarifErrorMessage = document.getElementById("error-message-tarif");
    const dataInchiriereInput = document.getElementById("filter-data-inchiriere");
    const dataReturnareInput = document.getElementById("filter-data-returnare");

    const currentYear = new Date().getFullYear();

    if (dataInchiriereInput) {
        const today = new Date().toISOString().split("T")[0];
        dataInchiriereInput.setAttribute("min", today);
    }

    window.handleDateChange = () => {
        const dataInchiriereValue = dataInchiriereInput?.value;
        const dataReturnareValue = dataReturnareInput?.value;

        if (dataInchiriereValue) {
            const inchiriereDate = new Date(dataInchiriereValue);
            inchiriereDate.setDate(inchiriereDate.getDate() + 1);
            const minReturnDate = inchiriereDate.toISOString().split("T")[0];

            dataReturnareInput.disabled = false;
            dataReturnareInput.setAttribute("min", minReturnDate);

            if (dataReturnareValue && dataReturnareValue < minReturnDate) {
                dataReturnareInput.value = "";
            }
        } else {
            dataReturnareInput.disabled = true;
            dataReturnareInput.value = "";
        }
        updateMasini();
    };

    if (sortDropdown) {
        sortDropdown.addEventListener("change", updateMasini);
    }

    if(marcaDropdown){
        marcaDropdown.addEventListener("change", () => {
            const marcaId = marcaDropdown.value;

            modelDropdown.innerHTML = '<option value="">Toate</option>';
            modelDropdown.disabled = true;

            if (!marcaId) {
                modelDropdown.disabled = true;
                modelDropdown.innerHTML = '<option value="" disabled selected>Selectează Marca</option>';
            } else {
                modelDropdown.disabled = false;

                fetch(`/get-models/${marcaId}`)
                    .then(response => response.json())
                    .then(data => {
                        modelDropdown.innerHTML = '<option value="">Toate</option>';

                        data.modele.forEach(model => {
                            const option = document.createElement("option");
                            option.value = model.id;
                            option.textContent = model.denumire;
                            modelDropdown.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error("Eroare la încărcarea modelelor:", error);
                        modelDropdown.innerHTML = '<option value="" disabled selected>Eroare la încărcare</option>';
                        modelDropdown.disabled = true;
                    });
            }

            updateMasini();
        });
    }

    if(modelDropdown){
        modelDropdown.addEventListener("change", updateMasini);
    }

    if(anFabricatieInput){
        anFabricatieInput.addEventListener("input", () => {
            const an = parseInt(anFabricatieInput.value);
    
            if (an && (an < 1990 || an > currentYear)) {
                anErrorMessage.style.display = "block";
                anErrorMessage.textContent = `Anul de fabricație trebuie să fie între 1990 și ${currentYear}!`;
                masiniContainer.innerHTML = "";
            } else {
                anErrorMessage.style.display = "none";
                updateMasini();
            }
        });   
    }

    if(tarifMaximInput){
        tarifMaximInput.addEventListener("input", () => {
            const tarif = parseInt(tarifMaximInput.value);

            if (tarif && tarif <= 0) {
                tarifErrorMessage.style.display = "block";
                tarifErrorMessage.textContent = `Tariful nu poate fi mai mic sau egal cu 0!`;
                masiniContainer.innerHTML = "";
            } else {
                tarifErrorMessage.style.display = "none";
                updateMasini();
            }
        });
    }
    
    if(orasDropdown){
        orasDropdown.addEventListener("change", updateMasini);
    }

    function syncRezervaButtons() {
        const rezervareButtons = document.querySelectorAll(".rezerva2-btn");
        rezervareButtons.forEach((button) => {
            const masinaId = button.dataset.masinaId;
            if (selectedMasini.has(masinaId)) {
                button.textContent = "Anulează";
                button.classList.add("anuleaza-btn");
            } else {
                button.textContent = "Rezervă";
                button.classList.remove("anuleaza-btn");
            }
        });

        const confirmButton = document.querySelector(".rezerva-confirmare-btn");
        if (confirmButton) {
            confirmButton.style.display = selectedMasini.size > 0 ? "block" : "none";
            const urlParams = new URLSearchParams();
            selectedMasini.forEach((id) => urlParams.append("masini_ids", id));
            confirmButton.href = `/rezervare?${urlParams.toString()}`;
        }
    }

    function attachRezervaEvents() {
        const rezervareButtons = document.querySelectorAll(".rezerva2-btn");
        rezervareButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const masinaId = button.dataset.masinaId;

                if (selectedMasini.has(masinaId)) {
                    selectedMasini.delete(masinaId);
                } else {
                    selectedMasini.add(masinaId);
                }

                syncRezervaButtons();
            });
        });
    }
    
    function updateMasini() {
        const marcaId = document.getElementById("filter-marca")?.value || "";
        const modelId = document.getElementById("filter-model")?.value || "";
        const anFabricatie = document.getElementById("filter-an-fabricatie")?.value || "";
        const tarifMaxim = document.getElementById("filter-tarif-maxim")?.value || "";
        const oras = document.getElementById("filter-oras")?.value || "";
        const dataInchiriere = document.getElementById("filter-data-inchiriere")?.value || "";
        const dataReturnare = document.getElementById("filter-data-returnare")?.value || "";
        const editMode = document.getElementById("edit-toggle-btn")?.classList.contains("active");
        const sortStatus = sortDropdown?.value || "all";

        const masiniContainer = document.querySelector(".masini-container");
        const url = `/rezerva-masina?edit_mode=${editMode}&sort_status=${sortStatus}&marca_id=${marcaId}&model_id=${modelId}&an_fabricatie=${anFabricatie}&tarif_maxim=${tarifMaxim}&oras=${oras}&data_inchiriere=${dataInchiriere}&data_returnare=${dataReturnare}`;
    
        if (anFabricatie && (anFabricatie < 1990 || anFabricatie > new Date().getFullYear())) {
            masiniContainer.innerHTML = "";
            return;
        }
    
        if (tarifMaxim && tarifMaxim <= 0) {
            masiniContainer.innerHTML = "";
            return;
        }
    
        fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Eroare la fetch: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                masiniContainer.innerHTML = "";
    
                if (data.masini.length === 0) {
                    masiniContainer.innerHTML = `
                        <div class="no-masini-container">
                            <p class="no-masini-text">Nicio mașină valabilă momentan!</p>
                        </div>
                    `;
                    return;
                }
    
                data.masini.forEach(masina => {
                    const masinaDiv = document.createElement("div");
                    masinaDiv.className = "masina-panou";
                    masinaDiv.innerHTML = `
                        <div class="imagine-panou">
                            <img src="${masina.Imagine_URL}" alt="${masina.Model}">
                        </div>
                        <div class="info-panou">
                            <p><strong>Marca:</strong> <span>${masina.Marca}</span></p>
                            <p><strong>Model:</strong> <span>${masina.Model}</span></p>
                            <p><strong>An fabricație:</strong> <span>${masina.An_Fabricatie}</span></p>
                            <p><strong>Tarif:</strong> <span>${masina.Tarif} RON/zi</span></p>
                            <p><strong>Locație:</strong> <span>${masina.Nume_Locatie}</span></p>
                            <p><strong>Adresă:</strong> <span>${masina.Adresa}</span></p>
                            ${
                                editMode
                                    ? `<p><strong>Activă:</strong> <span>${masina.IsActive}</span></p>`
                                    : ""
                            }
                        </div>
                        ${
                            editMode
                                ? masina.IsActive === "Da"
                                    ? `<button class="delete-btn" onclick="showDeactivateModal(${masina.ID_Masina})">Dezactivează</button>`
                                    : `<button class="activate-btn" onclick="showActivateModal(${masina.ID_Masina})">Activează</button>`
                                : `<button class="rezerva2-btn" data-masina-id="${masina.ID_Masina}">Rezervă</button>`
                        }
                    `;
                    masiniContainer.appendChild(masinaDiv);
                });
                attachRezervaEvents();
            })
            .catch(error => {
                console.error("Eroare la fetch:", error);
                masiniContainer.innerHTML = `
                    <div class="error-container">
                        <p class="error-text">Eroare la încărcarea mașinilor. Vă rugăm să încercați din nou mai târziu.</p>
                    </div>
                `;
            });
    }
    
    document.addEventListener("DOMContentLoaded", () => {
        attachRezervaEvents();
        syncRezervaButtons();
    });
    
});

document.addEventListener("DOMContentLoaded", () => {
    const masinaSelect = document.getElementById("id_masina");
    const tarifInput = document.getElementById("update_tarif");
    const locatieSelect = document.getElementById("update_id_locatie");
    const previewImage2 = document.getElementById("preview-image2");

    const previewImage = document.getElementById("preview-image");
    const imagineInput = document.getElementById("imagine");
    const imagineInput2 = document.getElementById("imagine2");

    if (imagineInput2) {
        imagineInput2.disabled = true;
    }

    if (masinaSelect) {
        masinaSelect.addEventListener("change", () => {
            const selectedOption = masinaSelect.options[masinaSelect.selectedIndex];
            let imagineUrl = selectedOption.getAttribute("data-imagine");
            const tarif = selectedOption.getAttribute("data-tarif");
            const idLocatie = selectedOption.getAttribute("data-id-locatie");

            if (imagineUrl && imagineUrl.startsWith("website/")) {
                imagineUrl = imagineUrl.replace("website/", "/");
            }

            

            tarifInput.value = tarif || "";
            locatieSelect.value = idLocatie || "";
            previewImage2.src = imagineUrl || "/static/photos/default.png";

            if (masinaSelect.value) {
                imagineInput2.disabled = false;
            } else {
                imagineInput2.disabled = true;
            }
        });
    }
    
    if (imagineInput) {
        imagineInput.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                previewImage.src = "/static/photos/default.png";
            }
        });
    }

    if (imagineInput2) {
        imagineInput2.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage2.src = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                previewImage2.src = "/static/photos/default.png";
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const deleteModal = document.getElementById("delete-modal");
    const deleteMessage = document.getElementById("delete-message");
    const deleteConfirmBtn = document.getElementById("delete-confirm-btn");

    window.showDeleteModal = (masinaId) => {
        deleteMessage.textContent = `Ești sigur că vrei să ștergi mașina? 
        Aceasta va șterge toate rezervările și facturile asociate.`;
        deleteModal.style.display = "block";

        deleteConfirmBtn.onclick = () => {
            deleteMasina(masinaId);
        };
    };

    window.closeDeleteModal = () => {
        deleteModal.style.display = "none";
    };

    function deleteMasina(masinaId) {
        fetch('/realdelete-masina', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_masina: masinaId })
        })
            .then((response) => {
                if (response.ok) {
                    response.json().then((data) => {
                        showSuccessPopupAfterReload(data.message || "Mașina a fost ștearsă cu succes!");
                    });
                } else {
                    response.json().then((data) => {
                        alert(data.error || "Eroare la ștergerea mașinii!");
                    });
                }
            })
            .catch((error) => console.error("Eroare:", error));
    }
    
    
});

document.addEventListener("DOMContentLoaded", () => {
    const successPopup = document.getElementById("successPopup");
    const successMessage = localStorage.getItem("successMessage");

    if (successMessage) {
        createSuccessPopup(successMessage);
        localStorage.removeItem("successMessage");
    }

    if (successPopup) {
        const url = new URL(window.location);
        if (url.searchParams.has("success_message")) {
            url.searchParams.delete("success_message");
            window.history.replaceState({}, document.title, url.toString());
        }
    }
});

function createSuccessPopup(message) {
    const popup = document.createElement("div");
    popup.className = "success-popup";
    popup.textContent = message;

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.style.opacity = "0";
        setTimeout(() => popup.remove(), 500);
    }, 5000);
}

function showSuccessPopupAfterReload(message) {
    localStorage.setItem("successMessage", message);
    location.reload();
}

function updateDeleteDetails() {
    const select = document.getElementById("id_masina_delete");
    const selectedOption = select.options[select.selectedIndex];
    const deleteButton = document.getElementById("delete-button");

    if (selectedOption && selectedOption.value) {
        const imagine = selectedOption.dataset.imagine;

        document.getElementById("delete-preview-image").src = imagine ? `${imagine}` : "/static/photos/default.png";
        document.getElementById("delete-car-details").style.display = "block";

        deleteButton.disabled = false;
    } else {
        document.getElementById("delete-car-details").style.display = "none";

        deleteButton.disabled = true;
    }
}

let currentIndex = 0;

const carousels = {};

function moveCarousel(direction, carouselId) {
    const carouselContainer = document.querySelector(`.carousel-container[data-carousel-id="${carouselId}"]`);
    if (!carouselContainer) return;

    const carousel = carouselContainer.querySelector('.carousel');
    const items = carouselContainer.querySelectorAll('.carousel-item');
    const totalItems = items.length;
    const itemsToShow = 3;
    const itemWidth = items[0].offsetWidth + 20;

    if (!carousels[carouselId]) {
        carousels[carouselId] = 0;
    }

    carousels[carouselId] += direction;

    if (carousels[carouselId] < 0) {
        carousels[carouselId] = totalItems - itemsToShow;
    } else if (carousels[carouselId] > totalItems - itemsToShow) {
        carousels[carouselId] = 0;
    }

    const transformValue = -carousels[carouselId] * itemWidth;
    carousel.style.transform = `translateX(${transformValue}px)`;
}

function showFacturaModal(button) {
    document.getElementById("factura-numar").textContent = button.dataset.numarFactura;
    document.getElementById("factura-data-plata").textContent = button.dataset.dataPlata;
    document.getElementById("factura-data-emitere").textContent = button.dataset.dataEmitere;
    document.getElementById("factura-suma").textContent = button.dataset.sumaTotala;

    document.getElementById("factura-modal").style.display = "block";
}

function closeFacturaModal() {
    document.getElementById("factura-modal").style.display = "none";
}

function sortRezervari() {
    const sortValue = document.getElementById("sort-dropdown").value;
    window.location.href = `/total-rezervari?sort=${sortValue}`;
}

let rezervareIdToDelete = null;

document.addEventListener("DOMContentLoaded", () => {
    window.showDeleteModal2 = function(rezervareId) {
        rezervareIdToDelete = rezervareId;
        const modal = document.getElementById("delete-modal");
        if (modal) {
            modal.style.display = "block";
        } else {
            console.error("Modalul cu ID-ul 'delete-modal' nu există în DOM.");
        }
    };
});

function closeDeleteModal2() {
    rezervareIdToDelete = null;
    document.getElementById("delete-modal").style.display = "none";
}

document.getElementById("confirm-delete-btn").addEventListener("click", function () {
    if (rezervareIdToDelete) {
        fetch(`/delete-rezervare/${rezervareIdToDelete}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Eroare la ștergerea rezervării");
                }
                return response.json();
            })
            .then((data) => {
                if (data.message) {
                    showSuccessPopupAfterReload(data.message);
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch((error) => console.error("Eroare:", error));
    }
});

function showSuccessPopupAfterReload(message) {
    localStorage.setItem("successMessage", message);
    location.reload();
}

document.addEventListener("DOMContentLoaded", () => {
    const dataInchiriere = document.getElementById("filter-data-inchiriere");
    const dataReturnare = document.getElementById("filter-data-returnare");

    window.handleDateChange = () => {
        if (dataInchiriere && dataReturnare) {
            const inchiriereValue = dataInchiriere.value;
            if (inchiriereValue) {
                const inchiriereDate = new Date(inchiriereValue);
                inchiriereDate.setDate(inchiriereDate.getDate() + 1);
                dataReturnare.disabled = false;
                dataReturnare.setAttribute("min", inchiriereDate.toISOString().split("T")[0]);

                if (dataReturnare.value < dataReturnare.min) {
                    dataReturnare.value = "";
                }
            } else {
                dataReturnare.disabled = true;
                dataReturnare.value = "";
            }
        }
    };
    handleDateChange();
});

