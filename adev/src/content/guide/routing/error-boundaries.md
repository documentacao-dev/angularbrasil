<!-- ia-translate: true -->
# Error boundaries no roteamento

IMPORTANT: Os error boundaries do Router estão em [developer preview](reference/releases#developer-preview).

Ao criar aplicações web, erros de runtime podem acontecer durante a inicialização de components, o carregamento de dados ou a renderização. O Angular Router permite isolar essas falhas em rotas individuais usando **error boundaries**, impedindo que um único component com problema derrube toda a casca da aplicação.

NOTE: Este guia trata do tratamento de erros no nível da route. Para capturar erros em trechos específicos do template de um component, veja o [guia do bloco `@boundary` de template](/guide/templates/error-boundaries).

## O que são error boundaries do router? {#what-are-router-error-boundaries}

Os error boundaries do router oferecem tratamento declarativo de erros no nível do outlet de route. Quando um component dentro de uma route lança um erro, como uma referência de recurso de rede que falhou, uma referência nula inesperada em um template ou um erro durante a injeção de dependência, o Angular Router captura o erro e exibe um component de fallback dedicado (`errorComponent`) no lugar da view que falhou.

Outlets irmãos, components de layout pai e cabeçalhos de navegação global continuam totalmente interativos e intactos.

## Configure um component de erro {#configure-an-error-component}

Para exibir uma UI de fallback customizada quando uma route falha, adicione a propriedade `errorComponent` à definição da route:

```ts {header:"app.routes.ts"}
import {Routes} from '@angular/router';
import {ProductDetails} from './product-details';
import {ProductErrorFallback} from './product-error-fallback';

export const routes: Routes = [
  {
    path: 'products/:id',
    component: ProductDetails,
    errorComponent: ProductErrorFallback,
  },
];
```

Quando você navegar para `/products/123`, se `ProductDetails` lançar um erro durante a criação ou a renderização, o Angular Router instancia `ProductErrorFallback` dentro do `<router-outlet>`.

NOTE: `errorComponent` só tem efeito depois que você habilita os error boundaries. Veja [Configuração global do error boundary](#global-error-boundary-configuration).

NOTE: Diferente dos components de route, que podem ser carregados sob demanda com `loadComponent`, o `errorComponent` precisa ser carregado de forma antecipada na configuração de rotas.

---

## Crie um component de fallback de erro {#create-an-error-fallback-component}

Um component de fallback de erro é um component Angular comum que pode receber os detalhes do erro capturado.

### Acesse os detalhes do erro com um input {#access-error-details-with-an-input}

Você pode receber o objeto do erro capturado declarando um input `error`:

```angular-ts {header:"product-error-fallback.ts"}
import {Component, input} from '@angular/core';

@Component({
  selector: 'app-product-error-fallback',
  template: `
    <div class="error-card">
      <h3>Falha ao carregar o produto</h3>
      <p>{{ error()?.message }}</p>
    </div>
  `,
})
export class ProductErrorFallback {
  readonly error = input<Error>();
}
```

NOTE: Se a configuração de rotas incluir parâmetros, query parameters ou dados de route chamados `error`, o `Error` de runtime capturado sempre tem precedência no input `error` de um component de erro.

IMPORTANT: Se o próprio `errorComponent` lançar um erro durante a criação ou a renderização, o `RouterOutlet` não o captura de novo. A exceção sobe para fora do outlet até o `ErrorHandler` raiz (ou um [bloco `@boundary` de template](/guide/templates/error-boundaries) que o envolva), para evitar loops infinitos de erro.

## Binding de parâmetros e dados da route {#route-parameter-and-data-binding}

Ao usar `withComponentInputBinding()`, o Angular Router também associa os parâmetros da route e os dados estáticos aos inputs do `errorComponent`. Assim, você pode exibir informações contextuais na sua UI de erro:

```angular-ts {header:"product-error-fallback.ts"}
import {Component, input} from '@angular/core';

@Component({
  selector: 'app-product-error-fallback',
  template: `
    <div class="error-card">
      <h3>Falha ao carregar o produto #{{ id() }}</h3>
      <p>{{ error()?.message }}</p>
    </div>
  `,
})
export class ProductErrorFallback {
  readonly id = input<string>();
  readonly error = input<Error>();
}
```

## Configuração global do error boundary {#global-error-boundary-configuration}

Habilite os error boundaries do router na sua aplicação com o recurso `withErrorBoundaries` em `provideRouter`. Sem ele, o `errorComponent` de uma route é ignorado:

```ts {header:"app.config.ts"}
import {ApplicationConfig, inject} from '@angular/core';
import {provideRouter, withComponentInputBinding, withErrorBoundaries} from '@angular/router';
import {routes} from './app.routes';
import {GlobalErrorFallback} from './global-error-fallback';
import {AnalyticsService} from './analytics.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),
      withErrorBoundaries({
        // Component de fallback padrão para rotas que não definem o próprio errorComponent
        defaultErrorComponent: GlobalErrorFallback,

        // Hook global de telemetria, chamado sempre que um erro de route é capturado
        onError: (error, details) => {
          inject(AnalyticsService).logException(error, details);
        },
      }),
    ),
  ],
};
```

### Opções {#options}

| Opção                   | Tipo                                             | Descrição                                                                                                                             |
| ----------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `defaultErrorComponent` | `Type<unknown>`                                  | Component de fallback padrão a renderizar quando uma route sem `errorComponent` próprio lança um erro.                              |
| `onError`               | `(error: Error, details?: ErrorDetails) => void` | Callback global chamado sempre que qualquer erro é capturado por um error boundary do router. Ideal para enviar telemetria a serviços de monitoramento. |

---

## Redirecionando com `RedirectCommand` {#redirecting-with-redirectcommand}

Quando uma falha de autenticação ou uma condição nos dados exige navegar para outra página, components e resources de route podem lançar um `RedirectCommand`:

```angular-ts {header:"user-profile.ts"}
import {Component, inject, resource} from '@angular/core';
import {Router, RedirectCommand} from '@angular/router';

@Component({
  selector: 'app-user-profile',
  template: `...`,
})
export class UserProfile {
  private router = inject(Router);

  userData = resource({
    loader: async () => {
      const response = await fetch('/api/user');
      if (response.status === 401) {
        // Redireciona automaticamente para /login quando não autorizado
        throw new RedirectCommand(this.router.parseUrl('/login'));
      }
      return response.json();
    },
  });
}
```

Quando um `RedirectCommand` é lançado:

1. O `RouterOutlet` captura o comando e inicia a navegação para o destino de redirecionamento especificado.
2. Se existirem outlets aninhados ou blocos de error boundary de template, o Angular deduplica o comando para garantir que a navegação seja disparada apenas uma vez.
3. O component de erro (se configurado) é renderizado durante a transição.

NOTE: Se um `RedirectCommand` for lançado e nenhum `errorComponent` estiver configurado, o router inicia a navegação e intencionalmente descarta o erro, para que ele não seja registrado como falha pelo `ErrorHandler` global.

## Escopo de error boundaries x erros de navegação {#error-boundary-scope-vs-navigation-errors}

Vale entender a diferença entre **erros da camada de view** e **erros do pipeline de navegação**:

- **Erros da camada de view (error boundaries)**: acontecem dentro de construtores de components, injeção de dependência, hooks do ciclo de vida (`ngOnInit`), expressões de template e loaders de `resource()` de components. Eles são capturados pelo `RouterOutlet`, que exibe o `errorComponent`.
- **Erros do pipeline de navegação (`NavigationError`)**: acontecem antes da ativação da route, como falhas em guards `canActivate` / `canMatch` ou em funções `resolve` de dados da route. Eles interrompem a transição de navegação antes de chegar ao outlet e podem ser customizados com `withNavigationErrorHandler`.

NOTE: Quando um error boundary exibe um `errorComponent`, os guards `canDeactivate` configurados para essa route são executados ao sair dela. O guard recebe a instância ativa do `errorComponent` como parâmetro `component`. Se o seu guard acessar propriedades ou métodos específicos de um component, verifique o tipo do component ou trate a instância do component de erro com segurança.

## Próximos passos {#next-steps}

<docs-pill-row>
  <docs-pill href="/guide/templates/error-boundaries" title="Error boundaries em templates"/>
  <docs-pill href="/guide/routing/show-routes-with-outlets" title="Mostrando rotas com outlets"/>
  <docs-pill href="/guide/routing/redirecting-routes" title="Redirecionando rotas"/>
  <docs-pill href="/guide/routing/data-fetching-with-resources" title="Busca de dados com recursos"/>
</docs-pill-row>
