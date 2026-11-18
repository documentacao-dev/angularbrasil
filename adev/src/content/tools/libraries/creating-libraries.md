<!-- ia-translate: true -->

# Criando bibliotecas

Esta página oferece uma visão geral conceitual de como criar e publicar novas bibliotecas para estender a funcionalidade do Angular.

Se você perceber que precisa resolver o mesmo problema em mais de uma aplicação \(ou quer compartilhar sua solução com outros desenvolvedores\), você tem um candidato a biblioteca.
Um exemplo simples seria um botão que envia os usuários para o site da sua empresa, que seria incluído em todas as aplicações que sua empresa constrói.

## Começando {#getting-started}

Use o Angular CLI para gerar um novo esqueleto de biblioteca em um novo workspace com os seguintes comandos.

```shell

ng new my-workspace --no-create-application
cd my-workspace
ng generate library my-lib

```

<docs-callout title="Nomeando sua biblioteca">

Tenha muito cuidado ao escolher o nome da sua biblioteca se você pretende publicá-la depois em um registro de pacotes público, como o npm.
Veja [Publicando sua biblioteca](tools/libraries/creating-libraries#publishing-your-library).

Evite usar um nome com o prefixo `ng-`, como `ng-library`.
O prefixo `ng-` é uma palavra-chave reservada, usada pelo framework Angular e por suas bibliotecas.
O prefixo `ngx-` é preferido como convenção para indicar que a biblioteca é adequada para uso com Angular.
Ele também é uma ótima indicação para os consumidores do registro diferenciarem bibliotecas de diferentes frameworks JavaScript.

</docs-callout>

O comando `ng generate` cria a pasta `projects/my-lib` no seu workspace, que contém um component.

HELPFUL: Para mais detalhes sobre como um projeto de biblioteca é estruturado, consulte a seção [Arquivos do projeto de biblioteca](reference/configs/file-structure#library-project-files) do guia [Estrutura de arquivos do projeto](reference/configs/file-structure).

Use o modelo monorepo para usar o mesmo workspace com vários projetos.
Veja [Configurando para um workspace multiprojeto](reference/configs/file-structure#multiple-projects).

Quando você gera uma nova biblioteca, o arquivo de configuração do workspace, `angular.json`, é atualizado com um projeto do tipo `library`.

```json

"projects": {
  …
  "my-lib": {
    "root": "projects/my-lib",
    "sourceRoot": "projects/my-lib",
    "projectType": "library",
    "prefix": "lib",
    "architect": {
      "build": {
        "builder": "@angular/build:library",
        …

```

Faça o build, teste e lint do projeto com os comandos da CLI:

```shell

ng build my-lib --configuration development
ng test my-lib
ng lint my-lib

```

Observe que o builder configurado para o projeto é diferente do builder padrão dos projetos de aplicação.
Esse builder, entre outras coisas, garante que a biblioteca seja sempre construída com o [compilador AOT](tools/cli/aot-compiler).

Para tornar o código da biblioteca reutilizável, você precisa definir uma API pública para ele.
Essa "camada de usuário" define o que está disponível para os consumidores da sua biblioteca.
Um usuário da sua biblioteca deve conseguir acessar a funcionalidade pública \(como providers de services e funções utilitárias gerais\) por meio de um único caminho de import.

A API pública da sua biblioteca é mantida no arquivo `public-api.ts`, na pasta da biblioteca.
Tudo o que for exportado desse arquivo fica público quando a biblioteca é importada em uma aplicação.

Sua biblioteca deve fornecer documentação \(normalmente um arquivo README\) para instalação e manutenção.

## Pontos de entrada {#entry-points}

Um _entry point_ é um especificador de módulo do qual os consumidores importam, junto com a API pública que esse especificador expõe.
Toda biblioteca tem um _entry point primário_ e você pode adicionar quantos _entry points secundários_ quiser.

Você configura os entry points no arquivo `package.json` da biblioteca usando o campo `"exports"`.
A chave `"."` define o entry point primário e aponta para o arquivo TypeScript que exporta a API pública:

```json {header: "projects/my-lib/package.json"}
{
  "name": "my-lib",
  "version": "0.0.1",
  "exports": {
    ".": "./src/public-api.ts"
  },
  …
}
```

Os consumidores importam o entry point primário pelo nome do pacote:

```ts
import {ThemeService} from 'my-lib';
```

Um entry point secundário é uma chave de subcaminho adicional em `"exports"` que aponta para o seu próprio arquivo de API pública.
Por exemplo, uma exportação `"./button"` torna `my-lib/button` disponível para os consumidores:

```ts
import {ButtonComponent} from 'my-lib/button';
```

Os pacotes do Angular usam essa mesma estrutura.
Por exemplo, `@angular/core` é o entry point primário, e `@angular/core/testing` é um entry point secundário do mesmo pacote.

HELPFUL: Para uma visão arquitetural de como os entry points habilitam o code splitting e definem os limites dos chunks no Formato de Pacote Angular, veja [Entrypoints e code splitting](tools/libraries/angular-package-format#entrypoints-and-code-splitting).

### Adicionando um entry point secundário {#adding-a-secondary-entry-point}

Use o [schematic `entry-point`](cli/generate/entry-point) para gerar um novo entry point secundário na sua biblioteca:

```shell
ng generate entry-point button --project my-lib
```

Você também pode gerar subcaminhos aninhados, como `testing/harness`:

```shell
ng generate entry-point testing/harness --project my-lib
```

Executar `ng generate entry-point button --project my-lib` faz as seguintes etapas:

1. Cria um diretório `button/src/` dentro da biblioteca, com o próprio arquivo `public-api.ts` e os arquivos iniciais do component:

   ```text
   projects/my-lib/
   ├── package.json
   ├── src/
   │   ├── public-api.ts         (primary entry point: my-lib)
   │   └── lib/
   │       ├── my-lib.spec.ts
   │       └── my-lib.ts
   └── button/
       └── src/
           ├── button.spec.ts
           ├── button.ts
           └── public-api.ts     (secondary entry point: my-lib/button)
   ```

1. Registra o subcaminho `"./button"` no `package.json` da biblioteca:

   ```json {header: "projects/my-lib/package.json"}
   {
     "name": "my-lib",
     "version": "0.0.1",
     "exports": {
       ".": "./src/public-api.ts",
       "./button": "./button/src/public-api.ts"
     },
     …
   }
   ```

1. Adiciona um mapeamento de path com curinga `"my-lib/*"` no `tsconfig.json` do workspace (se ainda não existir), para que as aplicações do mesmo workspace consigam resolver os entry points secundários a partir da saída construída da biblioteca:

   ```json {header: "tsconfig.json"}
   {
     "compilerOptions": {
       "paths": {
         "my-lib": ["./dist/my-lib"],
         "my-lib/*": ["./dist/my-lib/*"]
       }
     }
   }
   ```

   Como `"my-lib/*"` é um padrão com curinga, ele é adicionado na primeira vez que você gera um entry point secundário e cobre automaticamente todos os entry points secundários atuais e futuros, sem precisar atualizar o `tsconfig.json` de novo.

Durante o build, o `@angular/build:library` descobre todos os entry points pelo campo `"exports"` de `projects/my-lib/package.json`, compila e empacota cada entry point, e grava as condições de exportação `types` e `default` correspondentes em `dist/my-lib/package.json`.

## Refatorando partes de uma aplicação em uma biblioteca {#refactoring-parts-of-an-application-into-a-library}

Para tornar sua solução reutilizável, você precisa ajustá-la para que não dependa de código específico da aplicação.
Veja algumas coisas a considerar ao migrar funcionalidades da aplicação para uma biblioteca.

- Declarações como components e pipes devem ser projetadas como stateless, ou seja, não devem depender nem alterar variáveis externas.
  Se você depender de estado, precisa avaliar cada caso e decidir se se trata de estado da aplicação ou de um estado que a biblioteca deveria gerenciar.

- Quaisquer observables aos quais os components se inscrevem internamente devem ser limpos e descartados durante o ciclo de vida desses components
- Components devem expor suas interações por meio de inputs, para fornecer contexto, e de outputs, para comunicar eventos a outros components

- Verifique todas as dependências internas.
  - Para classes ou interfaces personalizadas usadas em components ou services, verifique se elas dependem de outras classes ou interfaces que também precisam ser migradas
  - Da mesma forma, se o código da sua biblioteca depende de um service, esse service precisa ser migrado
  - Se o código da sua biblioteca ou os templates dela dependerem de outras bibliotecas \(como o Angular Material, por exemplo\), você deve configurar sua biblioteca com essas dependências

- Considere como você fornece services às aplicações clientes.
  - Services devem declarar seus próprios providers, em vez de declará-los no NgModule ou em um component.
    Declarar um provider torna esse service _tree-shakable_.
    Essa prática permite que o compilador deixe o service de fora do bundle caso ele nunca seja injetado na aplicação que importa a biblioteca.
    Para saber mais sobre isso, veja [Providers tree-shakable](guide/di/lightweight-injection-tokens).

  - Se você registrar providers globais de services, exponha uma função de provider `provideXYZ()`.
  - Se sua biblioteca fornecer services opcionais que podem não ser usados por todas as aplicações clientes, dê suporte adequado a tree-shaking nesse caso usando o [padrão de design de token leve](guide/di/lightweight-injection-tokens)

## Integrando com a CLI usando schematics de geração de código {#integrating-with-the-cli-using-code-generation-schematics}

Uma biblioteca normalmente inclui _código reutilizável_ que define components, services e outros artefatos do Angular \(pipes, directives\) que você importa em um projeto.
Uma biblioteca é empacotada em um pacote npm para publicação e compartilhamento.
Esse pacote também pode incluir schematics que fornecem instruções para gerar ou transformar código diretamente no seu projeto, da mesma forma que a CLI cria um component genérico com `ng generate component`.
Um schematic empacotado com uma biblioteca pode, por exemplo, fornecer ao Angular CLI as informações necessárias para gerar um component que configura e usa um recurso específico, ou um conjunto de recursos, definido naquela biblioteca.
Um exemplo disso é o [schematic de navegação do Angular Material](https://material.angular.dev/guide/schematics#navigation-schematic), que configura o [BreakpointObserver](https://material.angular.dev/cdk/layout/overview#breakpointobserver) do CDK e o usa com os components [MatSideNav](https://material.angular.dev/components/sidenav/overview) e [MatToolbar](https://material.angular.dev/components/toolbar/overview) do Material.

Crie e inclua os seguintes tipos de schematics:

- Inclua um schematic de instalação para que `ng add` possa adicionar sua biblioteca a um projeto
- Inclua schematics de geração na sua biblioteca para que `ng generate` possa criar os artefatos definidos \(components, services, testes\) em um projeto
- Inclua um schematic de atualização para que `ng update` possa atualizar as dependências da sua biblioteca e fornecer migrações para mudanças incompatíveis em novas versões

O que você inclui na sua biblioteca depende da sua tarefa.
Por exemplo, você poderia definir um schematic para criar um dropdown pré-preenchido com dados fixos, mostrando como adicioná-lo a uma aplicação.
Se você quiser um dropdown que contenha valores diferentes passados a cada vez, sua biblioteca poderia definir um schematic para criá-lo com uma determinada configuração.
Os desenvolvedores poderiam então usar `ng generate` para configurar uma instância para a própria aplicação.

Suponha que você queira ler um arquivo de configuração e então gerar um formulário com base nessa configuração.
Se esse formulário precisar de personalização adicional pelo desenvolvedor que usa sua biblioteca, pode funcionar melhor como um schematic.
No entanto, se o formulário será sempre o mesmo e não precisar de muita personalização, você poderia criar um component dinâmico que recebe a configuração e gera o formulário.
Em geral, quanto mais complexa for a personalização, mais útil é a abordagem com schematics.

Para mais informações, veja a [Visão geral de Schematics](tools/cli/schematics) e [Schematics para bibliotecas](tools/cli/schematics-for-libraries).

## Publicando sua biblioteca {#publishing-your-library}

Use o Angular CLI e o gerenciador de pacotes npm para construir e publicar sua biblioteca como um pacote npm.

O Angular CLI usa o builder `@angular/build:library` para compilar seu código em pacotes no [Formato de Pacote Angular](tools/libraries/angular-package-format) que você pode publicar no npm.
Veja [Publicando bibliotecas](tools/libraries/creating-libraries#publishing-libraries) para informações sobre os formatos de distribuição suportados e orientações sobre como escolher o formato certo para sua biblioteca.

Você deve sempre construir bibliotecas para distribuição usando a configuração `production` (a configuração padrão do `ng build`).
Isso garante que a saída gerada use as otimizações apropriadas e o formato de pacote correto para o npm.

```shell

ng build my-lib
cd dist/my-lib
npm publish

```

## Gerenciando assets em uma biblioteca {#managing-assets-in-a-library}

Na sua biblioteca Angular, o distribuível pode incluir assets adicionais, como arquivos de tema, mixins Sass ou documentação \(como um changelog\).
Por padrão, o builder da biblioteca copia os arquivos `README.md` e `LICENSE*` da raiz da biblioteca para o diretório de saída, e incorpora como data URLs os assets referenciados por caminhos `url()` relativos nas folhas de estilo dos components.
Para copiar arquivos adicionais como parte do build, configure a [opção `assets`](reference/configs/workspace-config#assets-configuration) no target `build` da sua biblioteca em `angular.json`:

```json {header: "angular.json"}
{
  "projects": {
    "my-lib": {
      "architect": {
        "build": {
          "builder": "@angular/build:library",
          "options": {
            "tsConfig": "projects/my-lib/tsconfig.lib.json",
            "assets": [
              "projects/my-lib/CHANGELOG.md",
              "projects/my-lib/_index.scss",
              "projects/my-lib/prebuilt-themes",
              {
                "glob": "**/*.scss",
                "input": "projects/my-lib/src/theming",
                "output": "theming"
              }
            ]
          }
        }
      }
    }
  }
}
```

IMPORTANT: Ao incluir assets adicionais, como mixins Sass ou CSS pré-compilado, exponha-os no campo [`"exports"`](tools/libraries/angular-package-format#exports) do `package.json` da biblioteca.

O builder da biblioteca mescla os subcaminhos e as condições personalizadas de `"exports"` com os exports de entry point gerados, permitindo expor folhas de estilo ou condições personalizadas junto com os entry points TypeScript:

```json {header: "projects/my-lib/package.json"}
{
  "exports": {
    ".": {
      "sass": "./_index.scss",
      "default": "./src/public-api.ts"
    },
    "./theming": {
      "sass": "./theming/_theming.scss"
    },
    "./prebuilt-themes/indigo-pink.css": {
      "style": "./prebuilt-themes/indigo-pink.css"
    }
  }
}
```

## Dependências peer {#peer-dependencies}

Bibliotecas Angular devem listar como peer dependencies quaisquer dependências `@angular/*` das quais a biblioteca depende.
Isso garante que, quando os módulos pedirem o Angular, todos recebam exatamente o mesmo módulo.
Se uma biblioteca listar `@angular/core` em `dependencies` em vez de `peerDependencies`, ela pode acabar recebendo um módulo Angular diferente, o que faria sua aplicação quebrar.

## Usando sua própria biblioteca em aplicações {#using-your-own-library-in-applications}

Você não precisa publicar sua biblioteca no gerenciador de pacotes npm para usá-la no mesmo workspace, mas precisa construí-la primeiro.

Para usar sua própria biblioteca em uma aplicação:

- Construa a biblioteca.
  Você não pode usar uma biblioteca antes de construí-la.

```shell
  ng build my-lib
```

- Nas suas aplicações, importe da biblioteca pelo nome:

```ts
import {myExport} from 'my-lib';
```

### Construindo e reconstruindo sua biblioteca {#building-and-rebuilding-your-library}

A etapa de build é importante se você não publicou sua biblioteca como pacote npm e depois a instalou de volta na sua aplicação a partir do npm.
Por exemplo, se você clonar seu repositório git e executar `npm install`, seu editor mostrará os imports de `my-lib` como ausentes se você ainda não tiver construído a biblioteca.

HELPFUL: Quando você importa algo de uma biblioteca em uma aplicação Angular, o Angular procura um mapeamento entre o nome da biblioteca e uma localização no disco.
Ao instalar um pacote de biblioteca, o mapeamento fica na pasta `node_modules`.
Ao construir a sua própria biblioteca, ele precisa encontrar o mapeamento nos paths do seu `tsconfig`.

Gerar uma biblioteca com o Angular CLI adiciona automaticamente o caminho dela ao arquivo `tsconfig`.
O Angular CLI usa os paths do `tsconfig` para informar ao sistema de build onde encontrar a biblioteca.

Para mais informações, veja [Visão geral do mapeamento de paths](https://www.typescriptlang.org/docs/handbook/module-resolution.html#path-mapping).

Você pode reconstruir sua biblioteca sempre que fizer alterações nela, mas essa etapa extra leva tempo.
A funcionalidade de _builds incrementais_ melhora a experiência de desenvolvimento de bibliotecas.
Sempre que um arquivo é alterado, é executado um build parcial que emite os arquivos modificados.

Builds incrementais podem ser executados como um processo em segundo plano no seu ambiente de desenvolvimento.
Para aproveitar esse recurso, adicione a flag `--watch` ao comando de build:

```shell

ng build my-lib --watch

```

IMPORTANT: O comando `build` da CLI usa um builder diferente para bibliotecas (`@angular/build:library`) do que para aplicações (`@angular/build:application`).

As bibliotecas são compiladas e empacotadas de acordo com o [Formato de Pacote Angular](tools/libraries/angular-package-format), o que significa que o código-fonte TypeScript produz uma saída diferente em uma biblioteca construída do que em uma aplicação construída.

Por isso, uma aplicação que depende de uma biblioteca deve usar apenas mapeamentos de path do TypeScript que apontem para a _biblioteca construída_.
Os mapeamentos de path do TypeScript _não_ devem apontar para os arquivos `.ts` de código-fonte da biblioteca.

### Vinculando bibliotecas para desenvolvimento local {#linking-libraries-for-local-development}

Esta seção explica como usar o recurso de vinculação local do seu gerenciador de pacotes \(como [`npm link`](https://docs.npmjs.com/cli/v11/commands/npm-link) ou [`pnpm link`](https://pnpm.io/cli/link)\) para testar uma biblioteca Angular independente com uma aplicação externa durante o desenvolvimento local, sem depender da estrutura de workspace monorepo nem da publicação no registro do npm.

NOTE: Se sua biblioteca e sua aplicação estiverem no mesmo workspace Angular \(uma configuração monorepo\), o fluxo padrão de monorepo cuida automaticamente da vinculação e costuma ser mais eficiente. Essa abordagem de vinculação local é mais indicada quando:

- Você está desenvolvendo uma biblioteca independente e precisa testar as mudanças com uma aplicação externa que a consome.
- Você está testando mudanças da biblioteca em uma aplicação consumidora fora do workspace monorepo.

#### Configurando a aplicação consumidora {#configuring-the-consuming-application}

Para usar bibliotecas vinculadas, você precisa configurar o arquivo `angular.json` da sua aplicação com as seguintes definições:

```json
{
  "projects": {
    "your-app": {
      "architect": {
        "build": {
          "builder": "@angular/build:application",
          "options": {
            "preserveSymlinks": true
          },
          "configurations": {
            "development": {
              "sourceMap": {
                "scripts": true,
                "styles": true,
                "vendor": true
              }
            }
          }
        },
        "serve": {
          "builder": "@angular/build:dev-server",
          "options": {
            "prebundle": {
              "exclude": ["my-lib"]
            }
          }
        }
      }
    }
  }
}
```

**Opções de configuração explicadas:**

- `preserveSymlinks: true`: instrui o sistema de build a seguir os symlinks criados pelo comando de vinculação do seu gerenciador de pacotes, em vez de resolver para a localização original do symlink. Isso é essencial para evitar múltiplas cópias dos mesmos pacotes de dependência.
- `sourceMap.vendor`: habilitar source maps de vendor (especialmente `vendor: true`) facilita a depuração do código da biblioteca vinculada.
- `prebundle.exclude`: por padrão, o Angular CLI pode fazer o pré-bundle de todas as dependências do node. Excluir sua biblioteca garante que o código-fonte vinculado seja observado e reconstruído corretamente quando houver mudanças.

## Publicando bibliotecas {#publishing-libraries}

Há dois formatos de distribuição a serem usados ao publicar uma biblioteca:

| Formatos de distribuição    | Detalhes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :-------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Partial-Ivy \(recomendado\) | Contém código portátil que pode ser consumido por aplicações Ivy construídas com qualquer versão do Angular a partir da v12.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Full-Ivy                    | Contém instruções privadas do Angular Ivy. A ABI do compilador (as APIs internas de runtime chamadas por essas instruções) é estável entre versões de patch, mas pode mudar entre versões minor. Este formato exige que a biblioteca e a aplicação sejam construídas com a mesma versão minor do Angular. Ele é útil em ambientes onde todo o código da biblioteca e da aplicação é construído a partir do código-fonte ou compartilhado em uma arquitetura de microfrontends. |

Para publicar no npm, use o formato partial-Ivy, pois ele é estável entre versões de patch do Angular.

Evite compilar bibliotecas com código full-Ivy se você estiver publicando no npm, porque as instruções Ivy geradas dependem da ABI do compilador, que pode mudar entre versões minor.

## Garantindo compatibilidade de versão da biblioteca {#ensuring-library-version-compatibility}

A versão do Angular usada para construir uma aplicação deve sempre ser igual ou superior às versões do Angular usadas para construir qualquer uma das suas bibliotecas dependentes.
Por exemplo, se você tiver uma biblioteca que usa o Angular versão 13, a aplicação que depende dessa biblioteca deve usar o Angular versão 13 ou posterior.
O Angular não oferece suporte a usar uma versão anterior na aplicação.

Se você pretende publicar sua biblioteca no npm, construa com a configuração `production`, que define `"compilationMode": "partial"` por padrão para gerar código partial-Ivy.
Esse formato parcial é estável entre diferentes versões do Angular, por isso é seguro publicá-lo no npm.
O código nesse formato é processado durante o build da aplicação usando a mesma versão do compilador Angular, garantindo que a aplicação e todas as suas bibliotecas usem uma única versão do Angular.

Evite compilar bibliotecas com código full-Ivy se você estiver publicando no npm, porque as instruções Ivy geradas dependem da ABI do compilador, que pode mudar entre versões minor.

Se você nunca publicou um pacote no npm antes, precisa criar uma conta de usuário.
Leia mais em [Publicando pacotes npm](https://docs.npmjs.com/getting-started/publishing-npm-packages).

## Consumindo código partial-Ivy fora do Angular CLI {#consuming-partial-ivy-code-outside-the-angular-cli}

Uma aplicação instala muitas bibliotecas Angular do npm no diretório `node_modules`.
No entanto, o código dessas bibliotecas não pode ser empacotado diretamente junto com a aplicação construída, pois ele não está totalmente compilado.
Para concluir a compilação, use o linker do Angular.

Para aplicações que não usam o Angular CLI, o linker está disponível como um plugin [Babel](https://babeljs.io).
O plugin deve ser importado de `@angular/compiler-cli/linker/babel`.

O plugin Babel do linker do Angular oferece suporte a cache de build, o que significa que as bibliotecas só precisam ser processadas pelo linker uma única vez, independentemente de outras operações do npm.

Exemplo de integração do plugin em um build [webpack](https://webpack.js.org) personalizado, registrando o linker como um plugin do [Babel](https://babeljs.io) com o [babel-loader](https://webpack.js.org/loaders/babel-loader/#options):

<docs-code header="webpack.config.mjs" path="adev/src/content/examples/angular-linker-plugin/webpack.config.mjs" region="webpack-config"/>

HELPFUL: O Angular CLI integra o plugin do linker automaticamente. Assim, se os consumidores da sua biblioteca estiverem usando a CLI, eles podem instalar bibliotecas Ivy nativas do npm sem nenhuma configuração adicional.
