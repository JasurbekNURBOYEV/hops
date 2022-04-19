const WebApp = window.Telegram.WebApp;

function lightenDarkenColor(col = "#000000", amt) {
    var usePound = false;
    if (col[0] == "#") {
        col = col.slice(1);
        usePound = true;
    }
    var num = parseInt(col, 16);
    var r = (num >> 16) + amt;
    if (r > 255) {
        r = 255;
    } else if (r < 0) {
        r = 0;
    }
    var b = ((num >> 8) & 0x00ff) + amt;
    if (b > 255) {
        b = 255;
    } else if (b < 0) {
        b = 0;
    }
    var g = (num & 0x0000ff) + amt;
    if (g > 255) {
        g = 255;
    } else if (g < 0) {
        g = 0;
    }
    return (usePound ? "#" : "") + (g | (b << 8) | (r << 16)).toString(16);
}

function setCssProperty(name, value) {
    var root = document.documentElement;
    if (root && root.style && root.style.setProperty) {
        root.style.setProperty("--tg-" + name, value);
    }
}

const surfaceColor = lightenDarkenColor(
    WebApp.themeParams.bg_color,
    WebApp.colorScheme == "light" ? -10 : 10
);

setCssProperty("theme-surface-color", surfaceColor);

const Components = {
    TagCard: ({
        id,
        name,
        author,
        asked_count,
        subscribers_count,
        is_subscribed,
    }) => `
        <div class="card-container" style={{background-color: ${""}}}>
            <header class="card-header">
                <h5 class="tag-name">
                    #${name.match(/.{1,20}/g).join(" ")}
                </h5>

                <div class="switch">
                    <label class="switch-label">
                        <input class="switch-toggle" type="checkbox" data-tag="${id}" data-action="${
        is_subscribed ? "disabled" : "enabled"
    }" ${is_subscribed ? "checked" : ""} />

                        <div class="switch-base">
                            <div class="switch-handle"></div>
                        </div>
                    </label>
                </div>
            </header>

            <div class="card-footer">
                <div class="with-icon author">
                    <svg
                        class="icon"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M15.25 6C15.25 7.79493 13.7949 9.25 12 9.25V10.75C14.6234 10.75 16.75 8.62335 16.75 6H15.25ZM12 9.25C10.2051 9.25 8.75 7.79493 8.75 6H7.25C7.25 8.62335 9.37665 10.75 12 10.75V9.25ZM8.75 6C8.75 4.20507 10.2051 2.75 12 2.75V1.25C9.37665 1.25 7.25 3.37665 7.25 6H8.75ZM12 2.75C13.7949 2.75 15.25 4.20507 15.25 6H16.75C16.75 3.37665 14.6234 1.25 12 1.25V2.75ZM9 13.75H15V12.25H9V13.75ZM15 20.25H9V21.75H15V20.25ZM9 20.25C7.20507 20.25 5.75 18.7949 5.75 17H4.25C4.25 19.6234 6.37665 21.75 9 21.75V20.25ZM18.25 17C18.25 18.7949 16.7949 20.25 15 20.25V21.75C17.6234 21.75 19.75 19.6234 19.75 17H18.25ZM15 13.75C16.7949 13.75 18.25 15.2051 18.25 17H19.75C19.75 14.3766 17.6234 12.25 15 12.25V13.75ZM9 12.25C6.37665 12.25 4.25 14.3766 4.25 17H5.75C5.75 15.2051 7.20507 13.75 9 13.75V12.25Z"
                            
                        />
                    </svg>
                    ${author ?? ""}
                </div>
                
                <div class="card-right">
                    <div class="with-icon questions">
                        <svg
                            class="icon"
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M4.0404 7.13287C4.77451 7 5.74936 7 7.22222 7H8.77778C10.9558 7 12.0448 7 12.8766 7.42964C13.6084 7.80757 14.2033 8.4106 14.5761 9.15232C15 9.99554 15 11.0994 15 13.3071V15.4348C15 15.6552 15 15.7655 14.9956 15.8586C14.9253 17.3646 14.0255 18.6473 12.7481 19.2486M4.0404 7.13287C3.68896 7.19648 3.39269 7.29055 3.12337 7.42964C2.39163 7.80757 1.7967 8.4106 1.42386 9.15232C1 9.99554 1 11.0994 1 13.3071V16.6406C1 18.2828 2.31338 19.6141 3.93351 19.6141H4.40154C5.00751 19.6141 5.42186 20.2345 5.19681 20.8048C4.87911 21.6098 5.79383 22.3377 6.48993 21.8337L8.5205 20.3635C8.54121 20.3485 8.55157 20.341 8.56175 20.3337C9.21041 19.8704 9.98339 19.6193 10.7769 19.6142C10.7894 19.6141 10.806 19.6141 10.8392 19.6141C11.0818 19.6141 11.2031 19.6141 11.295 19.6097C11.8125 19.5849 12.3032 19.4581 12.7481 19.2486M4.0404 7.13287C4.09617 6.08171 4.22894 5.35029 4.54497 4.73005C5.02433 3.78924 5.78924 3.02433 6.73005 2.54497C7.79961 2 9.19974 2 12 2H14C16.8003 2 18.2004 2 19.27 2.54497C20.2108 3.02433 20.9757 3.78924 21.455 4.73005C22 5.79961 22 7.19974 22 10V14.2283C22 16.3114 20.3114 18 18.2283 18H17.6266C16.8475 18 16.3147 18.7869 16.6041 19.5103C17.0126 20.5314 15.8365 21.4546 14.9415 20.8154L12.7481 19.2486"
                                strokeWidth="1.5"
                            />
                            <path
                                d="M6 14C6 14.5523 5.55228 15 5 15C4.44772 15 4 14.5523 4 14C4 13.4477 4.44772 13 5 13C5.55228 13 6 13.4477 6 14Z"
                                
                            />
                            <path
                                d="M9 14C9 14.5523 8.55228 15 8 15C7.44772 15 7 14.5523 7 14C7 13.4477 7.44772 13 8 13C8.55228 13 9 13.4477 9 14Z"
                                
                            />
                            <path
                                d="M12 14C12 14.5523 11.5523 15 11 15C10.4477 15 10 14.5523 10 14C10 13.4477 10.4477 13 11 13C11.5523 13 12 13.4477 12 14Z"
                                
                            />
                        </svg>
                        ${asked_count}
                    </div>

                    <div class="with-icon subscribers">
                        <svg
                            class="icon"
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M14.25 7.75C14.25 8.99264 13.2426 10 12 10V11.5C14.0711 11.5 15.75 9.82107 15.75 7.75H14.25ZM12 10C10.7574 10 9.75 8.99264 9.75 7.75H8.25C8.25 9.82107 9.92893 11.5 12 11.5V10ZM9.75 7.75C9.75 6.50736 10.7574 5.5 12 5.5V4C9.92893 4 8.25 5.67893 8.25 7.75H9.75ZM12 5.5C13.2426 5.5 14.25 6.50736 14.25 7.75H15.75C15.75 5.67893 14.0711 4 12 4V5.5ZM9 14.5H15V13H9V14.5ZM15 19H9V20.5H15V19ZM9 19C7.75736 19 6.75 17.9926 6.75 16.75H5.25C5.25 18.8211 6.92893 20.5 9 20.5V19ZM17.25 16.75C17.25 17.9926 16.2426 19 15 19V20.5C17.0711 20.5 18.75 18.8211 18.75 16.75H17.25ZM15 14.5C16.2426 14.5 17.25 15.5074 17.25 16.75H18.75C18.75 14.6789 17.0711 13 15 13V14.5ZM9 13C6.92893 13 5.25 14.6789 5.25 16.75H6.75C6.75 15.5074 7.75736 14.5 9 14.5V13Z"
                                
                            />
                            <path
                                d="M7.75214 10.3887C7.59441 10.1353 7.29846 10 7 10C5.75736 10 4.75 8.99264 4.75 7.75C4.75 6.50736 5.75736 5.5 7 5.5C7.29846 5.5 7.59441 5.36473 7.75214 5.11135C7.75912 5.10014 7.76613 5.08896 7.7732 5.07782C8.0358 4.66331 7.90275 4.0764 7.415 4.0227C7.27873 4.0077 7.14027 4 7 4C4.92893 4 3.25 5.67893 3.25 7.75C3.25 9.82107 4.92893 11.5 7 11.5C7.14027 11.5 7.27873 11.4923 7.415 11.4773C7.90275 11.4236 8.0358 10.8367 7.7732 10.4222C7.76614 10.411 7.75912 10.3999 7.75214 10.3887Z"
                                
                            />
                            <path
                                d="M4.70829 18.3169C4.59477 18.1275 4.39439 18 4.17359 18H4C2.75736 18 1.75 16.9926 1.75 15.75C1.75 14.5074 2.75736 13.5 4 13.5H4.17359C4.39439 13.5 4.59477 13.3725 4.70829 13.1831C4.98539 12.7208 4.68468 12 4.14569 12H4C1.92893 12 0.25 13.6789 0.25 15.75C0.25 17.8211 1.92893 19.5 4 19.5H4.14569C4.68469 19.5 4.98539 18.7792 4.70829 18.3169Z"
                                
                            />
                            <path
                                d="M16.2268 10.4222C15.9642 10.8367 16.0973 11.4236 16.585 11.4773C16.7213 11.4923 16.8597 11.5 17 11.5C19.0711 11.5 20.75 9.82107 20.75 7.75C20.75 5.67893 19.0711 4 17 4C16.8597 4 16.7213 4.0077 16.585 4.0227C16.0973 4.0764 15.9642 4.66331 16.2268 5.07782C16.2339 5.08896 16.2409 5.10014 16.2479 5.11134C16.4056 5.36472 16.7015 5.5 17 5.5C18.2426 5.5 19.25 6.50736 19.25 7.75C19.25 8.99264 18.2426 10 17 10C16.7015 10 16.4056 10.1353 16.2479 10.3887C16.2409 10.3999 16.2339 10.411 16.2268 10.4222Z"
                                
                            />
                            <path
                                d="M19.2917 18.3169C19.0146 18.7792 19.3153 19.5 19.8543 19.5H20C22.0711 19.5 23.75 17.8211 23.75 15.75C23.75 13.6789 22.0711 12 20 12H19.8543C19.3153 12 19.0146 12.7208 19.2917 13.1831C19.4052 13.3725 19.6056 13.5 19.8264 13.5H20C21.2426 13.5 22.25 14.5074 22.25 15.75C22.25 16.9926 21.2426 18 20 18H19.8264C19.6056 18 19.4052 18.1275 19.2917 18.3169Z"
                                
                            />
                        </svg>
                        ${subscribers_count}
                    </div>
                </div>
            </div>
        </div>
    `,
};

(function () {
    let searchParams = new URLSearchParams(window.location.search);

    const state = {
        enabled: [],
        disabled: [],
        user: searchParams.get("user"),
        page: 1,
        total: 0,
        size: 30,
        search: null,
        loading: false,
    };

    async function fetchTags({ user, page, size, search }) {
        const { data } = await axios.get("https://hops.nurboyev.uz/api/tags/", {
            params: {
                user,
                page,
                size,
                search,
            },
        });

        return data;
    }

    async function saveChanges({ user }) {
        WebApp.MainButton.showProgress();
        WebApp.MainButton.setParams({
            color: WebApp.themeParams.hint_color,
            text_color: WebApp.themeParams.bg_color,
            text: "SAQLANMOQDA...",
        });

        const { enabled, disabled } = state;

        const { data } = await axios.post(
            "https://hops.nurboyev.uz/api/tags/",
            {
                user,
                enabled,
                disabled,
            }
        );

        return data;
    }

    function addRemoveTag(tag, action) {
        if (!state[action].includes(tag)) {
            state[action].push(tag);
        } else {
            state[action] = state[action].filter((item) => item !== tag);
        }
    }

    function showHideMainButton() {
        if (state.enabled.length || state.disabled.length) {
            WebApp.MainButton.setParams({
                text: "SAQLASH",
            });
            WebApp.MainButton.show();
        } else {
            WebApp.MainButton.hide();
        }
    }

    function showLoading() {
        state.loading = true;
        $(".spinner").removeClass("hidden");
    }

    function hideLoading() {
        state.loading = false;
        $(".spinner").addClass("hidden");
    }

    async function showTags(page = state.page, search = state.search) {
        const tags = await fetchTags({
            user: state.user,
            size: state.size,
            page,
            search,
        });

        state.total = tags.count;

        tags.results.map((tag) => {
            $("#card-list").append(Components.TagCard(tag));
        });
    }

    function search() {
        const search = $(".search-bar input").val();

        if (search.length && search.length < 3) {
            return;
        }

        $(".card-list").empty();
        $(".hint").addClass("hidden");

        state.page = 1;
        state.search = search;

        showTags();
    }

    showTags();

    $(window).change((e) => {
        const checkbox = $(e.target);

        if (checkbox.hasClass("switch-toggle")) {
            const tagId = checkbox.data("tag");
            const action = checkbox.data("action");

            addRemoveTag(tagId, action);

            showHideMainButton();
        }

        console.log(checkbox);
    });

    $(".search-bar").submit((e) => {
        e.preventDefault();
        search();
    });

    WebApp.MainButton.onClick(function () {
        saveChanges({
            user: state.user,
        })
            .then(function () {
                WebApp.close();
            })
            .catch((error) => {
                WebApp.MainButton.setParams({
                    color: WebApp.themeParams.button_color,
                });
                WebApp.MainButton.hide();
            });
    });

    $(window).scroll(function () {
        if (
            $(window).scrollTop() >
            $(document).height() - WebApp.viewportStableHeight - 50
        ) {
            const { size, page, total } = state;

            if (!state.loading) {
                if (size * (page - 1) <= total) {
                    showLoading();

                    state.page++;

                    showTags().finally(() => {
                        hideLoading();
                    });
                } else {
                    $(".hint").removeClass("hidden");
                }
            }
        }
    });
})();
