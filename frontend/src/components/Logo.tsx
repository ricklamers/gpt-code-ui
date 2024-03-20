import "./Logo.css";
import logo from "../../public/assets/assistant.svg";


export default function Logo() {
  return (
    <>
    <div className="logo">
        <div className="wrapper">
            <div className="header">
            <img src={ logo } />
            </div>
            <div className="header">
            <p className="headline">GPT Code UI</p>
            </div>
        </div>
        <div className='github'>
            Built with ❤️
        </div>
        <div className='github'>
            using&nbsp;<a href='https://github.com/ricklamers/gpt-code-ui'>GPT-Code UI - v{import.meta.env.VITE_APP_VERSION}</a>
        </div>
    </div>
    </>
  );
}
