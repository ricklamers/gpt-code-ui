import "./Logo.css";
import logo from "../../public/assets/VM_VibrantMFilled09_Syellow_Sblue.svg";


export default function Logo() {
  return (
    <>
    <div className="logo">
        <div className="wrapper">
            <div className="header">
            <img src={ logo } />
            </div>
            <div className="header">
            <p className="headline">Code</p>
            <p className="headline">Impact</p>
            </div>
        </div>
        <div className='github'>
            Built with ❤️ by the AI & Quantum Lab
        </div>
        <div className='github'>
            using&nbsp;<a href='https://github.com/ricklamers/gpt-code-ui'>GPT-Code UI - v{import.meta.env.VITE_APP_VERSION}</a>
        </div>
    </div>
    </>
  );
}
