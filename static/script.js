// Função para buscar dados do backend e atualizar o dashboard
async function fetchData(period = "last_7d", startDate = null, endDate = null) {
    try {
        let url = `/data?period=${period}`;
        if (period === "custom" && startDate && endDate) {
            url += `&start_date=${startDate}&end_date=${endDate}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            console.error("Erro ao carregar dados:", data.error);
            return;
        }

        console.log("📊 [DEBUG] Dados recebidos no frontend:", data);

        document.getElementById("gasto").innerText = `R$ ${data.gasto.toFixed(2)}`;
        document.getElementById("resultados").innerText = data.resultados ?? "0"; 
        document.getElementById("custo-resultado").innerText = 
        data.resultados > 0 ? `R$ ${(data.gasto / data.resultados).toFixed(2)}` : "R$ 0,00";
        document.getElementById("cliques").innerText = data.cliques;
        document.getElementById("cpc").innerText = `R$ ${data.cpc.toFixed(2)}`;
        document.getElementById("cpm").innerText = `R$ ${data.cpm.toFixed(2)}`;
        document.getElementById("ctr").innerText = `${data.ctr.toFixed(2)}%`;

        // 🔹 Atualiza os valores de PageView
        document.getElementById("pageviews").innerText = data.pageviews;
        
        // Calcula o custo por PageView (evita divisão por zero)
        let custoPageview = data.pageviews > 0 ? (data.gasto / data.pageviews).toFixed(2) : 0;
        document.getElementById("custo-pageview").innerText = `R$ ${custoPageview}`;

        // Calcula Connect Rate (conversão de cliques para PageView)
        let connectRate = data.cliques > 0 ? ((data.pageviews / data.cliques) * 100).toFixed(2) : 0;
        document.getElementById("connect-rate").innerText = `${connectRate}%`;

    } catch (error) {
        console.error("Erro na requisição:", error);
    }
}

// 🔹 Garante que os dados são carregados ao iniciar
document.addEventListener("DOMContentLoaded", () => {
    fetchData();
});



// Adiciona eventos aos botões de período padrão
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('input[name="periodo"]').forEach((radio) => {
        radio.addEventListener("change", (event) => {
            fetchData(event.target.value);
        });
    });

    // Carrega os dados iniciais com o período padrão (Últimos 7 dias)
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


