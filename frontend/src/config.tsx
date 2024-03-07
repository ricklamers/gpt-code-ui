let resolvedWebAddress = import.meta.env.VITE_WEB_ADDRESS ? import.meta.env.VITE_WEB_ADDRESS : location.pathname;

const Config = {
    WEB_ADDRESS: resolvedWebAddress,
    API_ADDRESS: (resolvedWebAddress + "/api").replace(/\/\//g, "/"),
}

export default Config;