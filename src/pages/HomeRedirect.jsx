import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function HomeRedirect() {

    const navigate = useNavigate();

    useEffect(() => {

        async function checkSetup() {

            try {

                //TODO: Backend eklenince açılacak. const res = await api.get("/setup/status");
                /*
                if (res.data.setup_required) {
                    navigate("/setup");
                } else {
                    navigate("/login");
                }
                */
               navigate('/login');

            } catch (err) {
                console.error(err);
            }

        }

        checkSetup();

    }, []);

    return <div>Loading...</div>;
}