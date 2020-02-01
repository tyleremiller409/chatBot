import React from "react";
import axios from "axios";
import "./form.css";

class Form extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      question: "",
      badge: ""
    };

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleQuestionChange = event => {
    this.setState({
      question: event.target.value
    });
  };

  handleSubmit = event => {
    let question = this.state.question;
    let url = "http://127.0.0.1:5000/" + `${question}`;
    console.log(url);
    axios
      .get(url)
      .then(response => {
        console.log(response);
        this.setState({
          badge: response.data
        });
      })
      .catch(error => {
        console.log(error);
      });
    event.preventDefault();
  };

  render() {
    return (
      <div>
        <form className="form-inline" onSubmit={this.handleSubmit}>
          <div className="form-group m-auto">
            <label className="badge m-auto mb-2 tylerLabel">Ask me something!</label>
            <input
              className="w-100 mb-2 form-control"
              type="text"
              value={this.state.question}
              onChange={this.handleQuestionChange}
            />
            <button className="btn btn-dark btn-lg m-auto" type="submit">
              Ask!
            </button>
          </div>
        </form>
        <h1 className="mt-2">{this.state.badge}</h1>
      </div>
    );
  }
}

export default Form;

// everything works
