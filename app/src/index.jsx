import React from 'react';
import ReactDOM from 'react-dom';

console.log("Hello world");


class Clock extends React.Component {
    constructor(props) {
        super(props);
        this.state = {now: new Date()};
    }

    componentDidMount() {
        this.timerId = setInterval(()=>{this.tick(); }, 1000);
    }

    componentWillUnmount() {
        clearTimeout(this.timerId);
    }

    tick() {
        this.setState({now: new Date()});
    }

    render() {
        return <p>Welcome to my clock, the time now is <strong>{this.state.now.toString()}</strong></p>
    }
}

function clicked_me() {
    alert("you clicked the button!");
}


var root = document.createElement("div");
document.body.appendChild(root);

ReactDOM.render(
    <div>
        <Clock/>
        <button onClick={clicked_me}>HeyJude</button>
    </div>,
    root
);
