async function fetchData(period = "last_7d", startDate = null, endDate = null) {
    const spinner = document.getElementById("spinner");
    const erro = document.getElementById("erro");
    
    try {
        // Exibe spinner e limpa mensagem de erro antes de iniciar a requisição
        spinner.style.display = "block";
        erro.innerText = "";

        let url = `/data?period=${period}`;
        if (period === "custom" && startDate && endDate) {
            url += `&start_date=${startDate}&end_date=${endDate}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro HTTP! Status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        console.log("📊 [DEBUG] Dados recebidos no frontend:", data);

        // Atualiza os elementos com os dados
        document.getElementById("gasto").innerText = `R$ ${data.gasto.toFixed(2)}`;
        document.getElementById("resultados").innerText = data.resultados ?? "0";
        document.getElementById("custo-resultado").innerText =
            data.resultados > 0 ? `R$ ${(data.gasto / data.resultados).toFixed(2)}` : "R$ 0,00";
        document.getElementById("cliques").innerText = data.cliques;
        document.getElementById("cpc").innerText = `R$ ${data.cpc.toFixed(2)}`;
        document.getElementById("ctr").innerText = `${data.ctr.toFixed(2)}%`;
        document.getElementById("cpm").innerText = `R$ ${data.cpm.toFixed(2)}`;
        document.getElementById("pageviews").innerText = data.pageviews;
        document.getElementById("custo-pageview").innerText = 
            data.pageviews > 0 ? `R$ ${(data.gasto / data.pageviews).toFixed(2)}` : "R$ 0,00";

        document.getElementById("connect-rate").innerText = 
            data.cliques > 0 ? `${((data.pageviews / data.cliques) * 100).toFixed(2)}%` : "0%";

    } catch (error) {
        console.error("Erro na requisição:", error);
        erro.innerText = "Ocorreu um erro ao carregar os dados.";
    } finally {
        // Esconde spinner após a requisição (com sucesso ou erro)
        spinner.style.display = "none";
    }
}
document.getElementById("spinner").style.display = "none";
// Evento DOMContentLoaded combinado corretamente
document.addEventListener("DOMContentLoaded", () => {
    // Exibe spinner antes de buscar dados
    document.getElementById("spinner").style.display = "block";

    document.querySelectorAll('input[name="periodo"]').forEach((radio) => {
        radio.addEventListener("change", (event) => {
            fetchData(event.target.value);
        });
    });

    fetchData();
});



// Adiciona eventos aos botões de período padrão
document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll('input[name="periodo"]').forEach((radio) => {
        radio.addEventListener("change", (event) => {
            fetchData(event.target.value);
        });
    });
    fetchData();
});

// Inicializa o DateRangePicker
$(document).ready(function() {
    $('#date-range-picker').daterangepicker({
        locale: {
            format: 'DD/MM/YYYY',
            separator: ' - ',
            applyLabel: 'Aplicar',
            cancelLabel: 'Cancelar',
            fromLabel: 'De',
            toLabel: 'Até',
            customRangeLabel: 'Personalizado',
            daysOfWeek: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
            monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
            firstDay: 1
        },
        startDate: moment().subtract(1, 'days'), // Começa ontem
        endDate: moment().subtract(7, 'days'), // Agora conta 7 dias antes de ontem
        opens: 'center',
        ranges: {
            'Hoje': [moment(), moment()],
            '7D': [moment().subtract(7, 'days'), moment().subtract(1, 'days')], // 🔹 Agora pega de ontem para trás
            'Este Mês': [moment().startOf('month'), moment()],
            'Mês Passado': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }, function(start, end) {
        fetchData('custom', start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD'));
    });
});


