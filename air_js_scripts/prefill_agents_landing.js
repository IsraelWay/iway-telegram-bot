<script>
    $.urlParam = function(name){
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results==null){
           return null;
        }
        else{
           return decodeURI(results[1]) || 0;
        }
    }
    var referral = $.urlParam('referral');

    $(window).load(function () {
        var masaTechFormUrl = "https://web.miniextensions.com/IU2yZjTjRDXHafMWxsGW?prefill_%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B,%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5%20%D0%BC%D0%BD%D0%B5%20%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D0%B5%D1%81%D0%BD%D1%8B=Masa%20Tech&prefill_Status=Welcome+email&prefill_target=masa";
        var regularForm = "https://web.miniextensions.com/6ubpe1moMUpHFZ5RzODj?prefill_Status=Welcome+email";

        $("#miniExtIframe-6ubpe1moMUpHFZ5RzODj").attr("src", regularForm);

        if (window.location.href.includes("masa-tech")) {
            $("#miniExtIframe-6ubpe1moMUpHFZ5RzODj").attr("src", masaTechFormUrl);
            $("#embed-script-id").attr("src", "https://web.miniextensions.com/statics/embed.js?miniExtIframeId=miniExtIframe-IU2yZjTjRDXHafMWxsGW");
        }

        if (referral) {
            $("#miniExtIframe-6ubpe1moMUpHFZ5RzODj").attr("src", $("#miniExtIframe-6ubpe1moMUpHFZ5RzODj").attr("src") + "&prefill_Referral=" + referral);
        }
    });

</script>