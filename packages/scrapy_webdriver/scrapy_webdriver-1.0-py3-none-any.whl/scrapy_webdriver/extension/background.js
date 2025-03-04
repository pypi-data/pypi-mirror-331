
                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "vvyyimhm",
                            password: "vu4t6rhgy97x"
                        }
                    };
                }
                
                browser.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
                );
               