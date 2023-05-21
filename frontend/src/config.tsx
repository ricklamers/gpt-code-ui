let resolvedWebAddress = import.meta.env.VITE_WEB_ADDRESS ? import.meta.env.VITE_WEB_ADDRESS : "";

const Config = {
    WEB_ADDRESS: resolvedWebAddress,
    API_ADDRESS: resolvedWebAddress + "/api"
}

export default Config;