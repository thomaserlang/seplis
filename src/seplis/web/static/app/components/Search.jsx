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
        this.onClick = this.click.bind(this);
        this.state = {
            results: [],
            show: false,
            selectedResultId: null,
            selectedResultType: null,
        }
        this.requesting = null;
        this.selectedResultId = null;
        this.onDocumentClick = this.documentClick.bind(this);
    }

    componentDidMount() {        
        document.addEventListener('click', this.onDocumentClick);
    }

    componentWillUnmount() {
        document.removeEventListener('click', this.onDocumentClick);
    }

    documentClick(e) {
        if (!this.form.contains(e.target)) {
            this.setState({show: false});
        }
    }

    inputChanged(e) {
        if (this.requesting)
            this.requesting.abort();
        let val = e.target.value.trim();
        if (val == '') {
            this.setState({
                results: [],
                show: false,
                selectedResultId: null,
            });
            return;
        }
        this.requesting = request('/1/search', {
            query: {
                query: e.target.value.trim(),
            }
        }).done(data => {
            this.suggestNode.scrollTop = 0;
            this.setState({
                results: data,
                show: true,
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
                this.click()
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
                if ((result.id == this.state.selectedResultId) && (result.type == this.state.selectedResultType)) {
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
        let type = this.state.results[i].type;
        this.setState({
            selectedResultId: id,
            selectedResultType: type,
        });
        if (disableScroll) 
            return;
        let height = document.getElementById(`sresult-${type}-${id}`).offsetHeight;
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

    click() {
        if (this.state.selectedResultId) {
            if (this.state.selectedResultType == 'series')
                location.href = `/show/${this.state.selectedResultId}`
            else if (this.state.selectedResultType == 'movie')
                location.href = `/movie/${this.state.selectedResultId}`;
        }
    }

    resultClassName(result) {
        let className = 'result';
        if (result.id == this.state.selectedResultId)
            className += ' selected';
        return className;
    }

    render() {
        return (
            <form 
                id="search" 
                className="form-inline" 
                onSubmit={this.onSubmit}                
                ref={(ref) => this.form = ref}
            >
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
                    style={{display:this.state.show?'block':'none'}}
                >
                    {this.state.results.map(r => (
                        <div 
                            key={`${r.type}-${r.id}`}
                            id={`sresult-${r.type}-${r.id}`}
                            data-id={r.id}
                            className={this.resultClassName(r)}
                            onMouseOver={this.onMouseOver}
                            onMouseOut={this.onMouseOut}
                            onClick={this.onClick}
                        >
                            <div className="img">
                                <img 
                                    src={r.poster_image!=null?r.poster_image.url + '@SY100':''} 
                                />
                            </div>
                            <div className="title">
                                {r.title} ({r.release_date?r.release_date.substring(0, 4):''})
                            </div>
                        </div>
                    ))}
                </div>
            </form>
        )
    }
}

export default Search;