window.onload = function() {
  const mySelect = document.querySelector('#inse');
  if(mySelect){
    mySelect.addEventListener('change', function() {
      const selectedValue = mySelect.value;
      console.log(`Hai selezionato l'opzione con valore ${selectedValue}`);
      $.ajax({
        url: corsiByInsegnamentoUrl,
        data: { codice_insegnamento: selectedValue },
        success: function(data) {
          console.log(data);
          $('#codice').empty();
          $.each(data, function(i, corso) {
            $('#codice').append($('<option>').text(corso.codice));
          });
        }
      });
    });
  };
}    