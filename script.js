        

        //==
        let payPrice = 0;
        function totalclick(click, itemNumber) {
            const totalclick = document.getElementById('totalclick' + itemNumber);
            const price = document.getElementById('price' + itemNumber);
            const totalprice = document.getElementById('totalprice' + itemNumber);
            const sumvalue = parseInt(totalclick.innerText) + click;
            totalclick.innerText = sumvalue;
            const tprice = parseInt(price.innerText) * sumvalue;
            totalprice.innerText = tprice + '';

            // Update pay price
            payPrice = 0;
            for (let i = 1; i <= 36; i++) {
                const totalpriceElement = document.getElementById('totalprice' + i);
                payPrice += parseInt(totalpriceElement.innerText);
            }
            document.getElementById('pay').innerText = payPrice + '';
        }

        function searchItem(itemNumber) {
            const totalclickElement = document.getElementById('totalclick' + itemNumber);
            const totalpriceElement = document.getElementById('totalprice' + itemNumber);

            const itemDetails = {
                name: "Item " + itemNumber,
                quantity: parseInt(totalclickElement.innerText),
                price: totalpriceElement.innerText
            };

            if (itemDetails) {
                const itemTableBody = document.getElementById("itemTableBody");
                const newRow = document.createElement("tr");
                newRow.setAttribute("id", "row" + itemNumber);

                const nameCell = document.createElement("td");
                nameCell.textContent = itemDetails.name;
                const quantityCell = document.createElement("td");
                quantityCell.textContent = itemDetails.quantity;
                const priceCell = document.createElement("td");
                priceCell.textContent = itemDetails.price;

                const actionCell = document.createElement("td");
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "DELETE";
                deleteButton.onclick = function() {
                    deleteItem(itemNumber);
                };
                actionCell.appendChild(deleteButton);

                newRow.appendChild(nameCell);
                newRow.appendChild(quantityCell);
                newRow.appendChild(priceCell);
                newRow.appendChild(actionCell);

                itemTableBody.appendChild(newRow);
            } else {
                alert("Item details not found.");
            }
        }

        function deleteItem(itemNumber) {
            const row = document.getElementById("row" + itemNumber);
            row.parentNode.removeChild(row);
        }

         // existing JavaScript code

    // existing JavaScript code

  // Add event listeners for add-item-button and cancel-add-item button for each left-column_in section
  const addItemButtons = document.querySelectorAll('.add-item-button');
  const addItemForms = document.querySelectorAll('.add-item-form');
  const cancelAddItemButtons = document.querySelectorAll('.cancel-add-item');

  addItemButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      addItemForms.forEach(form => form.style.display = 'none');
      addItemForms[index].style.display = 'block';
    });
  });

  cancelAddItemButtons.forEach(button => {
    button.addEventListener('click', () => {
      addItemForms.forEach(form => form.style.display = 'none');
    });
  });

  const addItemButtonsInForm = document.querySelectorAll('.add-item');
  addItemButtonsInForm.forEach(button => {
    button.addEventListener('click', () => {
      const form = button.closest('.add-item-form');
      const imageInput = form.querySelector('.item-image');
      const imageFile = imageInput.files[0];
      const reader = new FileReader();

      reader.onload = (event) => {
        const itemName = form.querySelector('.item-name').value;
        const quantity = form.querySelector('.quantity').value;
        const price = form.querySelector('.price').value;

        // Create new cart-item div
        const newCartItem = `
          <div class="cart-item">
            <img src="${event.target.result}" alt="Item Image" height="100px" width="150px" >
            <p class="item-name">${itemName}</p>
            <p class="quantity">Quantity: <span id="totalclick${index}">${quantity}</span></p>
            <p class="price">Price: <span id="price${index}">${price}.00</span> Rs</p>
            <p class="total-price">Total Price: <span id="totalprice${index}">${quantity * price}.00</span> Rs</p>
            <div class="actions">
              <button class="add-item" onclick="totalclick(1, ${index})">ADD ITEM</button>
              <button class="remove-item" onclick="totalclick(-1, ${index})">REMOVE ITEM</button>
              <button class="search" onclick="searchItem(${index})">ADD TO CART</button>
            </div>
          </div>
        `;

        // Add the new cart-item div to the corresponding left-column_in section
        const leftColumnIn = button.closest('.left-column_in');
        leftColumnIn.appendChild(newCartItem);

        // Reset the form
        form.reset();
        form.style.display = 'none';
      };

      reader.readAsDataURL(imageFile);
    });
  }); 