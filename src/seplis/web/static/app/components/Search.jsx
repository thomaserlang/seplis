import React from 'react';
import {request} from 'api';

import './Search.scss';

const KEY_UP = 38;
const KEY_DOWN = 40;
const KEY_ENTER = 13;

class Search extends React.Component {

    constructor(props) {
        super(props);
        this.onInputChanged = this.inputChanged.bind(this);
        this.onKeyDown = this.keyDown.bind(this);
        this.onMouseOver = this.mouseOver.bind(this);
        this.onMouseOut = this.mouseOut.bind(this);
        this.onSubmit = this.submit.bind(this);
        this.state = {
            results: [],
            display: false,
            selectedResultId: null,
        }
        this.requesting = null;
        this.selectedResultId = null;
    }

    inputChanged(e) {
        if (this.requesting)
            this.requesting.abort();
        let val = e.target.value.trim();
        if (val == '') {
            this.setState({
                results: [],
                display: false,
                selectedResultId: null,
            });
            return;
        }
        this.requesting = request('/1/shows', {
            query: {
                title_suggest: e.target.value.trim(),
                per_page: 10,
                fields: 'title,premiered,poster_image',
            }
        }).success(data => {
            this.suggestNode.scrollTop = 0;
            this.setState({
                results: data,
                display: true,
                selectedResultId: null,
            });
            this.setNextSelectedId(0);
        });
    }

    keyDown(e) {
        switch (e.keyCode) {
            case KEY_UP:
                this.setNextSelectedId(-1);
                break;
            case KEY_DOWN: 
                this.setNextSelectedId(1);
                break;
            case KEY_ENTER:
                if (this.state.selectedResultId) {
                    location.href = `/show/${this.state.selectedResultId}`
                }
                break;
        }
    }

    mouseOver(e) {
        this.state.selectedResultId = parseInt(e.target.getAttribute('data-id'));
        this.setNextSelectedId(0, true);
    }

    mouseOut(e) {
        this.setState({selectedResultId: null});
    }

    setNextSelectedId(val, disableScroll) {
        if (this.state.results.length == 0)
            return;
        let i = -1;
        if (this.state.selectedResultId) {
            i = 0;
            for (let result of this.state.results) {
                if (result.id == this.state.selectedResultId) {
                    break;
                }
                i++;
            }
        }
        i = i + val;
        if (i < 0)
            i = 0;
        if (i > (this.state.results.length - 1))
            i = this.state.results.length - 1;
        let id = this.state.results[i].id;
        this.setState({
            selectedResultId: id,
        });
        if (disableScroll) 
            return;
        let height = document.getElementById('sresult-'+id).offsetHeight;
        if (((i+1) * height) > this.suggestNode.offsetHeight) {
            let p = Math.floor(this.suggestNode.offsetHeight / height);
            let g = (i-p+1);
            let l = this.suggestNode.offsetHeight % height;
            this.suggestNode.scrollTop = (g*height)+l;
        } else {
            this.suggestNode.scrollTop = 0;
        }
    }

    submit(e) {
        e.preventDefault();
    }

    resultClassName(result) {
        let className = 'row';
        if (result.id == this.state.selectedResultId)
            className += ' selected';
        return className;
    }

    render() {
        return (
            <form id="search" className="form-inline" onSubmit={this.onSubmit}>
                <input 
                    className="form-control" 
                    type="text" 
                    placeholder="Search" 
                    onChange={this.onInputChanged}
                    onKeyDown={this.onKeyDown}
                />
                <div 
                    className="suggest"
                    ref={(ref) => this.suggestNode = ref}
                >
                    {this.state.results.map(r => (
                        <a 
                            key={r.id}
                            id={`sresult-${r.id}`}
                            data-id={r.id}
                            href={`/show/${r.id}`} 
                            className={this.resultClassName(r)}
                            onMouseOver={this.onMouseOver}
                            onMouseOut={this.onMouseOut}
                        >
                            <div className="col-xs-2">
                                <img 
                                    src={r.poster_image!=null?r.poster_image.url + '@SY100':''} 
                                    width="100%"
                                />
                            </div>
                            <div className="col-sm-10">
                                {r.title}
                            </div>
                        </a>
                    ))}
                </div>
            </form>
        )
    }
}

export default Search;