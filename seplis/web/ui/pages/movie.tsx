import { useParams } from "react-router-dom";

export default function Movie() {
    const { movieId } = useParams()

    useEffect(() => {
        document.title = 'Home | SEPLIS'
    }, [])
    
    return <div>ID {movieId} </div>
}