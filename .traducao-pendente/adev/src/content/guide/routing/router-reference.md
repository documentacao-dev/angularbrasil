<<<<<<< pt
<!-- ia-translate: true -->

# Referência do Router

As seções a seguir destacam alguns conceitos e terminologias centrais do router.

## Eventos do router {#router-events}

Durante cada navegação, o `Router` emite eventos de navegação por meio da propriedade `Router.events`.
Esses eventos são mostrados na tabela a seguir.

| Evento do router                                          | Detalhes                                                                                                                                                                                                                    |
| :-------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`NavigationStart`](api/router/NavigationStart)           | Acionado quando a navegação começa.                                                                                                                                                                                         |
| [`RouteConfigLoadStart`](api/router/RouteConfigLoadStart) | Acionado antes de o `Router` fazer o lazy loading de uma configuração de route.                                                                                                                                             |
| [`RouteConfigLoadEnd`](api/router/RouteConfigLoadEnd)     | Acionado depois que uma route é carregada de forma preguiçosa (lazy).                                                                                                                                                       |
| [`RoutesRecognized`](api/router/RoutesRecognized)         | Acionado quando o Router analisa a URL e as routes são reconhecidas.                                                                                                                                                        |
| [`GuardsCheckStart`](api/router/GuardsCheckStart)         | Acionado quando o Router começa a fase de guards do roteamento.                                                                                                                                                             |
| [`ChildActivationStart`](api/router/ChildActivationStart) | Acionado quando o Router começa a ativar as routes filhas de uma route.                                                                                                                                                     |
| [`ActivationStart`](api/router/ActivationStart)           | Acionado quando o Router começa a ativar uma route.                                                                                                                                                                         |
| [`GuardsCheckEnd`](api/router/GuardsCheckEnd)             | Acionado quando o Router finaliza com sucesso a fase de guards do roteamento.                                                                                                                                               |
| [`ResolveStart`](api/router/ResolveStart)                 | Acionado quando o Router começa a fase de resolve do roteamento.                                                                                                                                                            |
| [`ResolveEnd`](api/router/ResolveEnd)                     | Acionado quando o Router finaliza com sucesso a fase de resolve do roteamento.                                                                                                                                              |
| [`ChildActivationEnd`](api/router/ChildActivationEnd)     | Acionado quando o Router termina de ativar as routes filhas de uma route.                                                                                                                                                   |
| [`ActivationEnd`](api/router/ActivationEnd)               | Acionado quando o Router termina de ativar uma route.                                                                                                                                                                       |
| [`NavigationEnd`](api/router/NavigationEnd)               | Acionado quando a navegação termina com sucesso.                                                                                                                                                                            |
| [`NavigationCancel`](api/router/NavigationCancel)         | Acionado quando a navegação é cancelada. Isso pode acontecer quando um Route Guard retorna false durante a navegação ou quando redireciona retornando um `UrlTree` ou `RedirectCommand`.                                     |
| [`NavigationError`](api/router/NavigationError)           | Acionado quando a navegação falha devido a um erro inesperado.                                                                                                                                                              |
| [`Scroll`](api/router/Scroll)                             | Representa um evento de rolagem.                                                                                                                                                                                            |

Quando você habilita o recurso `withDebugTracing`, o Angular registra esses eventos no console.

## Terminologia do router {#router-terminology}

Estes são os principais termos do `Router` e seus significados:

| Parte do router       | Detalhes                                                                                                                                                                                                                                                    |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Router`              | Exibe o component da aplicação para a URL ativa. Gerencia a navegação de um component para o próximo.                                                                                                                                                       |
| `provideRouter`       | Fornece os providers de service necessários para navegar pelas views da aplicação.                                                                                                                                                                          |
| `RouterModule`        | Um NgModule separado que fornece os providers de service e as directives necessárias para navegar pelas views da aplicação.                                                                                                                                 |
| `Routes`              | Define um array de Routes, cada uma mapeando um caminho de URL para um component.                                                                                                                                                                           |
| `Route`               | Define como o router deve navegar até um component com base em um padrão de URL. Routes podem incluir caminhos, components, routes filhas, guards, resolvers e resources.                                                                                  |
| `RouterOutlet`        | A directive \(`<router-outlet>`\) que marca onde o router exibe uma view.                                                                                                                                                                                   |
| `RouterLink`          | A directive para vincular um elemento HTML clicável a uma route. Clicar em um elemento com a directive `routerLink` vinculada a uma _string_ ou a um _array de parâmetros de link_ aciona uma navegação.                                                    |
| `RouterLinkActive`    | A directive para adicionar ou remover classes de um elemento HTML quando um `routerLink` associado, contido no elemento ou dentro dele, fica ativo ou inativo. Também pode definir o `aria-current` de um link ativo para melhorar a acessibilidade.         |
| `ActivatedRoute`      | Um service fornecido a cada component de route, que contém informações específicas da route, como parâmetros de route, dados estáticos, dados de resolve, resources de route, query parameters globais e o fragment global.                                 |
| `RouterState`         | O estado atual do router, incluindo uma árvore das routes atualmente ativadas, junto com métodos auxiliares para percorrer a árvore de routes.                                                                                                             |
| Array de parâmetros de link | Um array que o router interpreta como uma instrução de roteamento. Você pode vincular esse array a um `RouterLink` ou passá-lo como argumento para o método `Router.navigate`.                                                                          |
| Componente de roteamento | Um component Angular com um `RouterOutlet` que exibe views com base nas navegações do router.                                                                                                                                                           |

## `<base href>` {#base-href}

O router usa o [history.pushState](https://developer.mozilla.org/docs/Web/API/History_API/Working_with_the_History_API#adding_and_modifying_history_entries 'HTML5 browser history push-state') do navegador para a navegação.
O `pushState` permite personalizar os caminhos de URL dentro da aplicação; por exemplo, `localhost:4200/crisis-center`.
As URLs internas da aplicação podem ser indistinguíveis das URLs do servidor.

Os navegadores HTML5 modernos foram os primeiros a oferecer suporte a `pushState`, e é por isso que muitas pessoas se referem a essas URLs como URLs "estilo HTML5".

HELPFUL: A navegação no estilo HTML5 é o padrão do router.
Na seção [LocationStrategy e estilos de URL do navegador](guide/routing/common-router-tasks#locationstrategy-and-browser-url-styles), saiba por que o estilo HTML5 é preferível, como ajustar o comportamento dele e como mudar para o estilo mais antigo baseado em hash \(`#`), se necessário.

Você deve adicionar um [elemento `<base href>`](https://developer.mozilla.org/docs/Web/HTML/Element/base 'base href') ao `index.html` da aplicação para que o roteamento com `pushState` funcione.
O navegador usa o valor de `<base href>` para prefixar URLs relativas ao referenciar arquivos CSS, scripts e imagens.

Adicione o elemento `<base>` logo após a tag `<head>`.
Se a pasta `app` for a raiz da aplicação, como é nesta aplicação, defina o valor de `href` no `index.html` conforme mostrado aqui.
||||||| base_en
# Router reference

The following sections highlight some core router concepts and terminology.

## Router events

During each navigation, the `Router` emits navigation events through the `Router.events` property.
These events are shown in the following table.

| Router event                                              | Details                                                                                                                                                                |
| :-------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`NavigationStart`](api/router/NavigationStart)           | Triggered when navigation starts.                                                                                                                                      |
| [`RouteConfigLoadStart`](api/router/RouteConfigLoadStart) | Triggered before the `Router` lazy loads a route configuration.                                                                                                        |
| [`RouteConfigLoadEnd`](api/router/RouteConfigLoadEnd)     | Triggered after a route has been lazy loaded.                                                                                                                          |
| [`RoutesRecognized`](api/router/RoutesRecognized)         | Triggered when the Router parses the URL and the routes are recognized.                                                                                                |
| [`GuardsCheckStart`](api/router/GuardsCheckStart)         | Triggered when the Router begins the Guards phase of routing.                                                                                                          |
| [`ChildActivationStart`](api/router/ChildActivationStart) | Triggered when the Router begins activating a route's children.                                                                                                        |
| [`ActivationStart`](api/router/ActivationStart)           | Triggered when the Router begins activating a route.                                                                                                                   |
| [`GuardsCheckEnd`](api/router/GuardsCheckEnd)             | Triggered when the Router finishes the Guards phase of routing successfully.                                                                                           |
| [`ResolveStart`](api/router/ResolveStart)                 | Triggered when the Router begins the Resolve phase of routing.                                                                                                         |
| [`ResolveEnd`](api/router/ResolveEnd)                     | Triggered when the Router finishes the Resolve phase of routing successfully.                                                                                          |
| [`ChildActivationEnd`](api/router/ChildActivationEnd)     | Triggered when the Router finishes activating a route's children.                                                                                                      |
| [`ActivationEnd`](api/router/ActivationEnd)               | Triggered when the Router finishes activating a route.                                                                                                                 |
| [`NavigationEnd`](api/router/NavigationEnd)               | Triggered when navigation ends successfully.                                                                                                                           |
| [`NavigationCancel`](api/router/NavigationCancel)         | Triggered when navigation is canceled. This can happen when a Route Guard returns false during navigation, or redirects by returning a `UrlTree` or `RedirectCommand`. |
| [`NavigationError`](api/router/NavigationError)           | Triggered when navigation fails due to an unexpected error.                                                                                                            |
| [`Scroll`](api/router/Scroll)                             | Represents a scrolling event.                                                                                                                                          |

When you enable the `withDebugTracing` feature, Angular logs these events to the console.

## Router terminology

Here are the key `Router` terms and their meanings:

| Router part           | Details                                                                                                                                                                                                                                   |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Router`              | Displays the application component for the active URL. Manages navigation from one component to the next.                                                                                                                                 |
| `provideRouter`       | provides the necessary service providers for navigating through application views.                                                                                                                                                        |
| `RouterModule`        | A separate NgModule that provides the necessary service providers and directives for navigating through application views.                                                                                                                |
| `Routes`              | Defines an array of Routes, each mapping a URL path to a component.                                                                                                                                                                       |
| `Route`               | Defines how the router should navigate to a component based on a URL pattern. Routes can include paths, components, child routes, guards, resolvers, and resources.                                                                       |
| `RouterOutlet`        | The directive \(`<router-outlet>`\) that marks where the router displays a view.                                                                                                                                                          |
| `RouterLink`          | The directive for binding a clickable HTML element to a route. Clicking an element with a `routerLink` directive that's bound to a _string_ or a _link parameters array_ triggers a navigation.                                           |
| `RouterLinkActive`    | The directive for adding/removing classes from an HTML element when an associated `routerLink` contained on or inside the element becomes active/inactive. It can also set the `aria-current` of an active link for better accessibility. |
| `ActivatedRoute`      | A service that's provided to each route component that contains route specific information such as route parameters, static data, resolve data, route resources, global query parameters, and the global fragment.                        |
| `RouterState`         | The current state of the router including a tree of the currently activated routes together with convenience methods for traversing the route tree.                                                                                       |
| Link parameters array | An array that the router interprets as a routing instruction. You can bind that array to a `RouterLink` or pass the array as an argument to the `Router.navigate` method.                                                                 |
| Routing component     | An Angular component with a `RouterOutlet` that displays views based on router navigations.                                                                                                                                               |

## `<base href>`

The router uses the browser's [history.pushState](https://developer.mozilla.org/docs/Web/API/History_API/Working_with_the_History_API#adding_and_modifying_history_entries 'HTML5 browser history push-state') for navigation.
`pushState` lets you customize in-application URL paths; for example, `localhost:4200/crisis-center`.
The in-application URLs can be indistinguishable from server URLs.

Modern HTML5 browsers were the first to support `pushState` which is why many people refer to these URLs as "HTML5 style" URLs.

HELPFUL: HTML5 style navigation is the router default.
In the [LocationStrategy and browser URL styles](guide/routing/common-router-tasks#locationstrategy-and-browser-url-styles) section, learn why HTML5 style is preferable, how to adjust its behavior, and how to switch to the older hash \(`#`\) style, if necessary.

You must add a [`<base href>` element](https://developer.mozilla.org/docs/Web/HTML/Element/base 'base href') to the application's `index.html` for `pushState` routing to work.
The browser uses the `<base href>` value to prefix relative URLs when referencing CSS files, scripts, and images.

Add the `<base>` element just after the `<head>` tag.
If the `app` folder is the application root, as it is for this application, set the `href` value in `index.html` as shown here.
=======
# Router reference

The following sections highlight some core router concepts and terminology.

## Router events

During each navigation, the `Router` emits navigation events through the `Router.events` property.
These events are shown in the following table.

| Router event                                              | Details                                                                                                                                                                |
| :-------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`NavigationStart`](api/router/NavigationStart)           | Triggered when navigation starts.                                                                                                                                      |
| [`RouteConfigLoadStart`](api/router/RouteConfigLoadStart) | Triggered before the `Router` lazy loads a route configuration.                                                                                                        |
| [`RouteConfigLoadEnd`](api/router/RouteConfigLoadEnd)     | Triggered after a route has been lazy loaded.                                                                                                                          |
| [`RoutesRecognized`](api/router/RoutesRecognized)         | Triggered when the Router parses the URL and the routes are recognized.                                                                                                |
| [`GuardsCheckStart`](api/router/GuardsCheckStart)         | Triggered when the Router begins the Guards phase of routing.                                                                                                          |
| [`ChildActivationStart`](api/router/ChildActivationStart) | Triggered when the Router begins activating a route's children.                                                                                                        |
| [`ActivationStart`](api/router/ActivationStart)           | Triggered when the Router begins activating a route.                                                                                                                   |
| [`GuardsCheckEnd`](api/router/GuardsCheckEnd)             | Triggered when the Router finishes the Guards phase of routing successfully.                                                                                           |
| [`ResolveStart`](api/router/ResolveStart)                 | Triggered when the Router begins the Resolve phase of routing.                                                                                                         |
| [`ResolveEnd`](api/router/ResolveEnd)                     | Triggered when the Router finishes the Resolve phase of routing successfully.                                                                                          |
| [`ActivationEnd`](api/router/ActivationEnd)               | Triggered when the Router finishes activating a route.                                                                                                                 |
| [`ChildActivationEnd`](api/router/ChildActivationEnd)     | Triggered when the Router finishes activating a route's children.                                                                                                      |
| [`NavigationEnd`](api/router/NavigationEnd)               | Triggered when navigation ends successfully.                                                                                                                           |
| [`NavigationCancel`](api/router/NavigationCancel)         | Triggered when navigation is canceled. This can happen when a Route Guard returns false during navigation, or redirects by returning a `UrlTree` or `RedirectCommand`. |
| [`NavigationError`](api/router/NavigationError)           | Triggered when navigation fails due to an unexpected error.                                                                                                            |
| [`Scroll`](api/router/Scroll)                             | Represents a scrolling event.                                                                                                                                          |

When you enable the `withDebugTracing` feature, Angular logs these events to the console.

## Router terminology

Here are the key `Router` terms and their meanings:

| Router part           | Details                                                                                                                                                                                                                                   |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Router`              | Displays the application component for the active URL. Manages navigation from one component to the next.                                                                                                                                 |
| `provideRouter`       | provides the necessary service providers for navigating through application views.                                                                                                                                                        |
| `RouterModule`        | A separate NgModule that provides the necessary service providers and directives for navigating through application views.                                                                                                                |
| `Routes`              | Defines an array of Routes, each mapping a URL path to a component.                                                                                                                                                                       |
| `Route`               | Defines how the router should navigate to a component based on a URL pattern. Routes can include paths, components, child routes, guards, resolvers, and resources.                                                                       |
| `RouterOutlet`        | The directive \(`<router-outlet>`\) that marks where the router displays a view.                                                                                                                                                          |
| `RouterLink`          | The directive for binding a clickable HTML element to a route. Clicking an element with a `routerLink` directive that's bound to a _string_ or a _link parameters array_ triggers a navigation.                                           |
| `RouterLinkActive`    | The directive for adding/removing classes from an HTML element when an associated `routerLink` contained on or inside the element becomes active/inactive. It can also set the `aria-current` of an active link for better accessibility. |
| `ActivatedRoute`      | A service that's provided to each route component that contains route specific information such as route parameters, static data, resolve data, route resources, global query parameters, and the global fragment.                        |
| `RouterState`         | The current state of the router including a tree of the currently activated routes together with convenience methods for traversing the route tree.                                                                                       |
| Link parameters array | An array that the router interprets as a routing instruction. You can bind that array to a `RouterLink` or pass the array as an argument to the `Router.navigate` method.                                                                 |
| Routing component     | An Angular component with a `RouterOutlet` that displays views based on router navigations.                                                                                                                                               |

## `<base href>`

The router uses the browser's [history.pushState](https://developer.mozilla.org/docs/Web/API/History_API/Working_with_the_History_API#adding_and_modifying_history_entries 'HTML5 browser history push-state') for navigation.
`pushState` lets you customize in-application URL paths; for example, `localhost:4200/crisis-center`.
The in-application URLs can be indistinguishable from server URLs.

Modern HTML5 browsers were the first to support `pushState` which is why many people refer to these URLs as "HTML5 style" URLs.

HELPFUL: HTML5 style navigation is the router default.
In the [LocationStrategy and browser URL styles](guide/routing/common-router-tasks#locationstrategy-and-browser-url-styles) section, learn why HTML5 style is preferable, how to adjust its behavior, and how to switch to the older hash \(`#`\) style, if necessary.

You must add a [`<base href>` element](https://developer.mozilla.org/docs/Web/HTML/Element/base 'base href') to the application's `index.html` for `pushState` routing to work.
The browser uses the `<base href>` value to prefix relative URLs when referencing CSS files, scripts, and images.

Add the `<base>` element just after the `<head>` tag.
If the `app` folder is the application root, as it is for this application, set the `href` value in `index.html` as shown here.
>>>>>>> new_en

```html
<base href="/" />
```

### URLs HTML5 e o `<base href>` {#html5-urls-and-the-base-href}

As diretrizes a seguir fazem referência a diferentes partes de uma URL.
Este diagrama descreve a que essas partes se referem:

```text {hideCopy}
foo://example.com:8042/over/there?name=ferret#nose
\_/   \______________/\_________/ \_________/ \__/
 |           |            |            |        |
scheme    authority      path        query   fragment
```

Embora o router use a estratégia [HTML5 pushState](https://developer.mozilla.org/docs/Web/API/History_API#Adding_and_modifying_history_entries 'Browser history push-state') por padrão, você deve configurar essa estratégia com um `<base href>`.

A forma preferida de configurar a estratégia é adicionar uma tag [`<base href>`](https://developer.mozilla.org/docs/Web/HTML/Element/base 'base href') no `<head>` do `index.html`.

```angular-html
<base href="/" />
```

Sem essa tag, o navegador pode não conseguir carregar recursos \(imagens, CSS, scripts\) ao fazer "deep linking" na aplicação.

Alguns desenvolvedores podem não conseguir adicionar o elemento `<base>`, talvez por não terem acesso ao `<head>` ou ao `index.html`.

Esses desenvolvedores ainda podem usar URLs HTML5 seguindo estes dois passos:

1. Fornecer ao router um valor apropriado de `APP_BASE_HREF`.
1. Usar URLs raiz \(URLs com uma `authority`\) para todos os recursos web: CSS, imagens, scripts e arquivos HTML de template.
   - O `path` do `<base href>` deve terminar com "/", pois os navegadores ignoram os caracteres do `path` que vêm depois da "`/`" mais à direita
   - Se o `<base href>` incluir uma parte `query`, a `query` só é usada se o `path` de um link na página estiver vazio e não tiver `query`.
     Isso significa que uma `query` no `<base href>` só é incluída ao usar `HashLocationStrategy`.

   - Se um link na página for uma URL raiz \(tiver uma `authority`\), o `<base href>` não é usado.
     Dessa forma, um `APP_BASE_HREF` com uma authority fará com que todos os links criados pelo Angular ignorem o valor de `<base href>`.

   - Um fragment no `<base href>` _nunca_ é persistido

Para informações mais completas sobre como o `<base href>` é usado para construir URIs de destino, veja a seção sobre transformação de referências na [RFC](https://tools.ietf.org/html/rfc3986#section-5.2.2).

### `HashLocationStrategy` {#hashlocationstrategy}

Use `HashLocationStrategy` fornecendo `useHash: true` em um objeto como segundo argumento de `RouterModule.forRoot()` no `AppModule`.

```ts
providers: [provideRouter(appRoutes, withHashLocation())];
```

Ao usar `RouterModule.forRoot`, isso é configurado com `useHash: true` no segundo argumento: `RouterModule.forRoot(routes, {useHash: true})`.
