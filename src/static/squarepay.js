/** Javascript to handle the Square payments form.
 * Adapted from https://docs.connect.squareup.com/payments/sqpaymentform/setup
 * SqPaymentForm documentation at https://docs.connect.squareup.com/api/paymentform */

/*
 * function: requestCardNonce
 *
 * requestCardNonce is triggered when the "Pay with credit card" button is
 * clicked
 *
 * Modifying this function is not required, but can be customized if you
 * wish to take additional action when the form button is clicked.
 */
function requestCardNonce(event) {

    // Don't submit the form until SqPaymentForm returns with a nonce
    event.preventDefault();

    // Request a nonce from the SqPaymentForm object
    paymentForm.requestCardNonce();
}

// Create and initialize a payment form object
var paymentForm = new SqPaymentForm({

    // Initialize the payment form elements
    applicationId: applicationId,
    locationId: locationId,
    inputClass: 'sq-input',
    autoBuild: false,

    // Customize the CSS for SqPaymentForm iframe elements
    inputStyles: [{
        fontSize: '16px',
        fontFamily: 'Helvetica Neue',
        padding: '16px',
        color: '#373F4A',
        backgroundColor: 'transparent',
        lineHeight: '24px',
        placeholderColor: '#CCC',
        _webkitFontSmoothing: 'antialiased',
        _mozOsxFontSmoothing: 'grayscale'
    }],

    /* digital wallets are only supported by Square for accounts in the US :'( */
    applePay: false,
    masterpass: false,
    googlePay: false,

    // Initialize the credit card placeholders
    cardNumber: {
        elementId: 'sq-card-number',
        placeholder: '• • • •    • • • •    • • • •    • • • •'
    },
    cvv: {
        elementId: 'sq-cvv',
        placeholder: 'CVV'
    },
    expirationDate: {
        elementId: 'sq-expiration-date',
        placeholder: 'MM/YY'
    },

    /* postal code is not required in AU */
    postalCode: false,

    // SqPaymentForm callback functions
    callbacks: {
        /* callback function: createPaymentRequest
         * Triggered when: a digital wallet payment button is clicked. */
/*        createPaymentRequest: function () {

            return {
                requestShippingAddress: false,
                requestBillingInfo: false,
                currencyCode: "AUD",
                countryCode: "AU",
                total: {
                    label: "University Computer Club Inc.",
                    amount: "100",
                    pending: false
                },
                lineItems: [
                    {
                        label: "Subtotal",
                        amount: "100",
                        pending: false
                    }
                ]
            }
        },*/

        /* callback function: cardNonceResponseReceived
         * Triggered when: SqPaymentForm completes a card nonce request */
        cardNonceResponseReceived: function (errors, nonce, cardData) {
            if (errors) {
                // Log errors from nonce generation to the Javascript console
                console.log("cardNonceResponseReceived encountered errors:");
                errors.forEach(function (error) {
                    console.log('    ' + error.message);
                });

                return;
            }
            // Assign the nonce value to the hidden form field
            document.getElementById('card-nonce').value = nonce;

            // POST the nonce form to the payment processing page
            document.getElementById('nonce-form').submit();
        },

        /* callback function: unsupportedBrowserDetected
         * Triggered when: the page loads and an unsupported browser is detected */
        unsupportedBrowserDetected: function () {
            /* PROVIDE FEEDBACK TO SITE VISITORS */
        },

        /* callback function: inputEventReceived
         * Triggered when: visitors interact with SqPaymentForm iframe elements. */
        inputEventReceived: function (inputEvent) {
            var e = document.getElementById("error");
            switch (inputEvent.eventType) {
                case 'focusClassAdded':
                    /* HANDLE AS DESIRED */
                    break;
                case 'focusClassRemoved':
                    /* HANDLE AS DESIRED */
                    break;
                case 'errorClassAdded':
                    e.innerHTML = "Please fix card information errors before continuing.";
                    e.style.display = "block";
                    break;
                case 'errorClassRemoved':
                    /* HANDLE AS DESIRED */
                    e.style.display = "none";
                    break;
                case 'cardBrandChanged':
                    /* HANDLE AS DESIRED */
                    break;
                case 'postalCodeChanged':
                    /* HANDLE AS DESIRED */
                    break;
            }
        },

        /* callback function: paymentFormLoaded
         * Triggered when: SqPaymentForm is fully loaded */
        paymentFormLoaded: function () {
            /* HANDLE AS DESIRED */
            console.log("The form loaded!");
            btn = document.getElementById("sq-creditcard");
            btn.disabled = false;
        }
    }
});

document.addEventListener("DOMContentLoaded", function(event) {
    /* for testing, you can add ...?unsupported to the URL */
    if (SqPaymentForm.isSupportedBrowser() && !window.location.href.includes("unsupported")) {
        console.log("loading Square payment form...");
        paymentForm.build();
        paymentForm.recalculateSize();
    } else {
        console.log("not loading form: unsupported browser!");
    }
});