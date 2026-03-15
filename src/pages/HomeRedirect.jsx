import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

export default function HomeRedirect() {
    const navigate = useNavigate();
    const { isAuthenticated, isSetupRequired } = useAuthStore();

    useEffect(() => {
        if (isSetupRequired) {
            navigate("/setup");
        } else if (isAuthenticated) {
            navigate("/dashboard");
        } else {
            navigate("/login");
        }
    }, [isAuthenticated, isSetupRequired, navigate]);

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center">
            <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );
}